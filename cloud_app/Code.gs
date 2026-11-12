/**
 * Google Apps Script 云端比价系统服务 (Code.gs)
 * 绑定的 Google Drive 目录: Supplier_Crawler_Cloud (1uM4bqickgGQjoAf7v1cdlJ16mDhMDvxP)
 */
const FOLDER_ID = '1uM4bqickgGQjoAf7v1cdlJ16mDhMDvxP';
const DAT_FILE_ID = '1Wywu6NtTkiY5gUztbsmjoPuey8JvRLEC';
const ACCESS_PIN = '8888';
const PDF_INBOX_FOLDER = '待解析PDF';

function getAdminPin_() {
  const propPin = PropertiesService.getScriptProperties().getProperty('ACCESS_PIN');
  return (propPin && propPin.trim()) ? propPin.trim() : ACCESS_PIN;
}

function verifyPin_(pin) {
  if (String(pin || '').trim() !== getAdminPin_()) {
    throw new Error('管理 PIN 密码错误');
  }
}

function testAuth() {
  const folder = DriveApp.getFolderById(FOLDER_ID);
  folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  try {
    const datFile = DriveApp.getFileById(DAT_FILE_ID);
    datFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  } catch (e) {}
  const imgFolders = folder.getFoldersByName('images');
  if (imgFolders.hasNext()) {
    imgFolders.next().setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  }
  getOrCreateSubFolder_(folder, PDF_INBOX_FOLDER);
  Logger.log('✅ 授权与免密直链配置成功！文件夹: ' + folder.getName());
  return '✅ 授权成功！云盘文件夹、待解析PDF目录与图片直链已就绪。';
}

function doGet(e) {
  // 服务端模板直推引擎：在服务器端读取压缩数据包并直接嵌入 HTML
  // 避开浏览器的二次 fetch、CORS、重定向与 RPC 传输瓶颈，实现打开即加载！
  try {
    const datFile = getDatFile_();
    const b64Data = datFile ? datFile.getBlob().getDataAsString('ASCII') : '';

    const template = HtmlService.createTemplateFromFile('Index');
    template.catalogData = b64Data;

    return template.evaluate()
      .setTitle('供应商跨店比价系统')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  } catch (err) {
    return HtmlService.createHtmlOutput('<h3 style="font-family:sans-serif;padding:20px;color:#ef4444;">加载失败: ' + err.message + '</h3>');
  }
}

function getDatFile_() {
  try {
    return DriveApp.getFileById(DAT_FILE_ID);
  } catch (e) {
    const folder = DriveApp.getFolderById(FOLDER_ID);
    const files = folder.getFilesByName('catalog_db.dat');
    return files.hasNext() ? files.next() : null;
  }
}

function getOrCreateSubFolder_(parentFolder, name) {
  const it = parentFolder.getFoldersByName(name);
  if (it.hasNext()) return it.next();
  return parentFolder.createFolder(name);
}

function countInboxPdfs_(inboxFolder) {
  let count = 0;
  const rootFiles = inboxFolder.getFiles();
  while (rootFiles.hasNext()) {
    const f = rootFiles.next();
    if (!f.isTrashed() && f.getName().toLowerCase().endsWith('.pdf')) {
      count += 1;
    }
  }
  const subFolders = inboxFolder.getFolders();
  while (subFolders.hasNext()) {
    const sf = subFolders.next();
    const sfName = sf.getName();
    if (sfName === '无法识别' || sfName === '_unrecognized') continue;
    const sfFiles = sf.getFiles();
    while (sfFiles.hasNext()) {
      const f = sfFiles.next();
      if (!f.isTrashed() && f.getName().toLowerCase().endsWith('.pdf')) {
        count += 1;
      }
    }
  }
  return count;
}

function triggerGitHubWorkflow_(workflowFile, inputs) {
  const props = PropertiesService.getScriptProperties();
  const repo = (props.getProperty('GITHUB_REPO') || '').trim();
  const token = (props.getProperty('GITHUB_TOKEN') || '').trim();
  const branch = (props.getProperty('GITHUB_BRANCH') || 'main').trim();

  if (!repo || !token) {
    return {
      ok: false,
      configured: false,
      message: '尚未在 Script Properties 配置 GITHUB_REPO 或 GITHUB_TOKEN',
    };
  }

  const url = 'https://api.github.com/repos/' + repo + '/actions/workflows/' + workflowFile + '/dispatches';
  const payload = {
    ref: branch,
    inputs: inputs || {},
  };
  const resp = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });

  const code = resp.getResponseCode();
  if (code === 204 || (code >= 200 && code < 300)) {
    return {
      ok: true,
      configured: true,
      code: code,
      message: '已唤醒 GitHub Actions 工作流: ' + workflowFile,
    };
  }
  return {
    ok: false,
    configured: true,
    code: code,
    message: 'GitHub API 返回异常 (' + code + '): ' + resp.getContentText(),
  };
}

/**
 * 供 GAS 5 分钟定时触发器调用：零消耗轮询 Drive 的 `待解析PDF` 文件夹，
 * 仅当存在待解析 PDF 时才唤醒 GitHub Actions `pdf_ingest.yml`（空文件夹 0 分钟额度消耗）。
 */
function checkPdfInboxAndTrigger() {
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const inbox = getOrCreateSubFolder_(folder, PDF_INBOX_FOLDER);
  const count = countInboxPdfs_(inbox);
  if (count === 0) {
    Logger.log('待解析PDF为空，跳过唤醒 GitHub Actions。');
    return { ok: true, count: 0, triggered: false };
  }

  const props = PropertiesService.getScriptProperties();
  const nowMs = Date.now();
  const lastMs = Number(props.getProperty('LAST_PDF_DISPATCH_TS') || 0);
  if (nowMs - lastMs < 3 * 60 * 1000) {
    Logger.log('距上次唤醒不足3分钟，等待当前任务处理...');
    return { ok: true, count: count, triggered: false, reason: 'cooldown' };
  }

  const res = triggerGitHubWorkflow_('pdf_ingest.yml', { triggered_by: 'gas-poller' });
  if (res.ok) {
    props.setProperty('LAST_PDF_DISPATCH_TS', String(nowMs));
  }
  Logger.log(JSON.stringify(res));
  return { ok: res.ok, count: count, triggered: res.ok, detail: res };
}

function getCloudControlStatus() {
  const props = PropertiesService.getScriptProperties();
  const repo = (props.getProperty('GITHUB_REPO') || '').trim();
  const hasToken = Boolean((props.getProperty('GITHUB_TOKEN') || '').trim());
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const inbox = getOrCreateSubFolder_(folder, PDF_INBOX_FOLDER);
  const inboxCount = countInboxPdfs_(inbox);
  let hasWatchTrigger = false;
  try {
    const triggers = ScriptApp.getProjectTriggers();
    hasWatchTrigger = triggers.some((t) => t.getHandlerFunction() === 'checkPdfInboxAndTrigger');
  } catch (e) {}
  return {
    githubConfigured: Boolean(repo && hasToken),
    githubRepo: repo || '未配置',
    inboxPdfCount: inboxCount,
    inboxFolderUrl: inbox.getUrl(),
    hasWatchTrigger: hasWatchTrigger,
  };
}

function adminTriggerCrawl(pin) {
  verifyPin_(pin);
  return triggerGitHubWorkflow_('daily_crawl.yml', { suppliers: 'default' });
}

function adminTriggerPdf(pin) {
  verifyPin_(pin);
  return triggerGitHubWorkflow_('pdf_ingest.yml', { triggered_by: 'admin-ui' });
}

function uploadPdfToInbox(filename, base64Data, supplierHint, pin) {
  verifyPin_(pin);
  const cleanName = String(filename || 'catalog.pdf').replace(/[\\\/:*?"<>|]/g, '_');
  const raw = String(base64Data || '').replace(/^data:.*;base64,/, '');
  const bytes = Utilities.base64Decode(raw);
  const blob = Utilities.newBlob(bytes, 'application/pdf', cleanName);

  const rootFolder = DriveApp.getFolderById(FOLDER_ID);
  let targetFolder = getOrCreateSubFolder_(rootFolder, PDF_INBOX_FOLDER);
  const hint = String(supplierHint || '').trim();
  if (hint) {
    targetFolder = getOrCreateSubFolder_(targetFolder, hint);
  }
  const file = targetFolder.createFile(blob);
  const dispatch = triggerGitHubWorkflow_('pdf_ingest.yml', { triggered_by: 'webapp-upload' });
  if (dispatch.ok) {
    PropertiesService.getScriptProperties().setProperty('LAST_PDF_DISPATCH_TS', String(Date.now()));
  }
  return {
    ok: true,
    fileName: file.getName(),
    fileUrl: file.getUrl(),
    dispatch: dispatch,
  };
}

function setupPdfWatchTrigger(pin) {
  if (pin !== undefined) {
    verifyPin_(pin);
  }
  const existing = ScriptApp.getProjectTriggers();
  existing.forEach((t) => {
    if (t.getHandlerFunction() === 'checkPdfInboxAndTrigger') {
      ScriptApp.deleteTrigger(t);
    }
  });
  ScriptApp.newTrigger('checkPdfInboxAndTrigger')
    .timeBased()
    .everyMinutes(5)
    .create();
  return { ok: true, message: '✅ 已开启每 5 分钟自动检测 Drive「待解析PDF」文件夹！' };
}
