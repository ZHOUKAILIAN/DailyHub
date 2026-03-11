#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');
const querystring = require('querystring');

const SDK_URL = 'https://static.udache.com/common/trinity-login/2.0.5/login.min.js';
const SDK_CACHE_DIR = path.join(__dirname, '.cache');
const SDK_CACHE_PATH = path.join(SDK_CACHE_DIR, 'trinity-login.min.js');
const PASSPORT_DOMAIN = 'epassport.diditaxi.com.cn';

const DEFAULT_SOURCE = 'https://energy.xiaojukeji.com/epower/';

const DEFAULT_LOGIN_CONFIG = {
  lang: 'zh-CN',
  __method__: 'POST',
  role: 41,
  country_id: 156,
  country_calling_code: '+86',
  appid: 120084,
  api_version: '1.0.1',
  app_version: '2.0.5',
  origin_id: '1',
  _source: DEFAULT_SOURCE,
  scene: 1,
  code_type: 0,
};

const DEFAULT_SIGN_AUTH = {
  appId: 121358,
  amChannel: 1323124385,
  source: '1323124385',
  ttid: 'driver',
  bizLine: 250,
};

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token.startsWith('--')) {
      const key = token.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) {
        args[key] = true;
      } else {
        args[key] = next;
        i += 1;
      }
    } else {
      args._.push(token);
    }
  }
  return args;
}

function ensureCacheDir() {
  if (!fs.existsSync(SDK_CACHE_DIR)) {
    fs.mkdirSync(SDK_CACHE_DIR, { recursive: true });
  }
}

function download(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, (res) => {
      const status = Number(res.statusCode || 0);
      if ([301, 302, 303, 307, 308].includes(status) && res.headers.location) {
        resolve(download(res.headers.location));
        return;
      }
      if (status < 200 || status >= 300) {
        reject(new Error(`download failed: HTTP ${status}`));
        return;
      }
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => {
        body += chunk;
      });
      res.on('end', () => resolve(body));
    });
    req.on('error', reject);
  });
}

async function loadSdkBundle() {
  ensureCacheDir();
  if (fs.existsSync(SDK_CACHE_PATH) && fs.statSync(SDK_CACHE_PATH).size > 1024) {
    return fs.readFileSync(SDK_CACHE_PATH, 'utf8');
  }
  const content = await download(SDK_URL);
  fs.writeFileSync(SDK_CACHE_PATH, content, 'utf8');
  return content;
}

function extractModulesArray(bundle) {
  const start = bundle.indexOf('([function');
  const end = bundle.lastIndexOf('])});');
  if (start < 0 || end < 0 || end <= start) {
    throw new Error('cannot parse trinity login bundle modules array');
  }
  const arrSrc = bundle.slice(start + 1, end + 1);
  const modules = Function(`return ${arrSrc};`)();
  if (!Array.isArray(modules) || modules.length < 200) {
    throw new Error('invalid modules array');
  }
  return modules;
}

function createWebpackRequire(modules) {
  const cache = {};
  function req(id) {
    if (cache[id]) {
      return cache[id].exports;
    }
    const modFn = modules[id];
    if (typeof modFn !== 'function') {
      throw new Error(`module ${id} is not a function`);
    }
    const module = { exports: {}, i: id, l: false };
    cache[id] = module;
    modFn.call(module.exports, module, module.exports, req);
    module.l = true;
    return module.exports;
  }
  return req;
}

function toInt(value, fallback) {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }
  const x = Number(value);
  return Number.isFinite(x) ? Math.trunc(x) : fallback;
}

function normalizePhone(raw) {
  return String(raw || '').replace(/\s+/g, '');
}

function buildCommonConfig(args) {
  return {
    ...DEFAULT_LOGIN_CONFIG,
    role: toInt(args.role, DEFAULT_LOGIN_CONFIG.role),
    appid: toInt(args.appid, DEFAULT_LOGIN_CONFIG.appid),
    scene: toInt(args.scene, DEFAULT_LOGIN_CONFIG.scene),
    code_type: toInt(args.code_type, DEFAULT_LOGIN_CONFIG.code_type),
    _source: String(args.source || DEFAULT_LOGIN_CONFIG._source),
  };
}

function postPassport(pathname, data) {
  const body = querystring.stringify(data);
  const options = {
    hostname: PASSPORT_DOMAIN,
    path: pathname,
    method: 'POST',
    headers: {
      'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'content-length': Buffer.byteLength(body),
      origin: 'https://energy.xiaojukeji.com',
      referer: 'https://energy.xiaojukeji.com/',
    },
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let text = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => {
        text += chunk;
      });
      res.on('end', () => {
        let json;
        try {
          json = JSON.parse(text);
        } catch (err) {
          json = null;
        }
        resolve({
          status: Number(res.statusCode || 0),
          headers: res.headers,
          text,
          json,
        });
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function buildSignAuth(ticket, args) {
  const t = String(ticket || '');
  return {
    ticket: t,
    token: t,
    tokenId: t,
    appId: toInt(args.sign_app_id, DEFAULT_SIGN_AUTH.appId),
    amChannel: toInt(args.sign_am_channel, DEFAULT_SIGN_AUTH.amChannel),
    source: String(args.sign_source || DEFAULT_SIGN_AUTH.source),
    ttid: String(args.sign_ttid || DEFAULT_SIGN_AUTH.ttid),
    bizLine: toInt(args.sign_biz_line, DEFAULT_SIGN_AUTH.bizLine),
    cityId: toInt(args.city_id, 2),
  };
}

async function callPassportApi(callName, param, signer, apiMap) {
  const q = JSON.stringify(param);
  const data = { q };
  const wsgsig = signer(data);
  const apiPath = apiMap[callName];
  if (!apiPath) {
    throw new Error(`unknown callName: ${callName}`);
  }
  const pathname = `${apiPath}?wsgsig=${encodeURIComponent(String(wsgsig))}`;
  const resp = await postPassport(pathname, data);
  return {
    call: callName,
    path: apiPath,
    status: resp.status,
    json: resp.json,
    text: resp.text,
    traceid: resp.json && resp.json.traceid ? resp.json.traceid : undefined,
  };
}

function output(obj) {
  process.stdout.write(`${JSON.stringify(obj, null, 2)}\n`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];
  if (!cmd || ['gatekeeper', 'send-code', 'login-by-code', 'get-captcha', 'verify-captcha'].indexOf(cmd) === -1) {
    output({
      ok: false,
      error: 'usage',
      message: 'cmd must be one of: gatekeeper | send-code | login-by-code | get-captcha | verify-captcha',
    });
    process.exitCode = 2;
    return;
  }

  const phone = normalizePhone(args.phone);
  if (!phone) {
    output({ ok: false, error: 'missing_phone', message: '--phone is required' });
    process.exitCode = 2;
    return;
  }

  const bundle = await loadSdkBundle();
  const modules = extractModulesArray(bundle);
  const req = createWebpackRequire(modules);
  const signerExport = req(193);
  const signer = typeof signerExport === 'function' ? signerExport : signerExport.default;
  if (typeof signer !== 'function') {
    throw new Error('cannot resolve wsgsig signer');
  }
  const apiMapExport = req(195);
  const apiMap = apiMapExport.default || apiMapExport;

  const common = buildCommonConfig(args);
  const baseParam = {
    ...common,
    cell: phone,
  };

  if (cmd === 'gatekeeper') {
    const gate = await callPassportApi('gatekeeper', baseParam, signer, apiMap);
    output({ ok: true, phone, result: gate });
    return;
  }

  if (cmd === 'send-code') {
    const gate = await callPassportApi('gatekeeper', baseParam, signer, apiMap);
    let scene = baseParam.scene;
    const loginType = gate.json && gate.json.roles && gate.json.roles[0] ? Number(gate.json.roles[0].login_type) : NaN;
    if (Number.isFinite(loginType) && loginType > 0) {
      scene = loginType;
    }
    const send = await callPassportApi('codeMT', { ...baseParam, scene, code_type: baseParam.code_type }, signer, apiMap);
    output({ ok: true, phone, scene, gatekeeper: gate, sendCode: send });
    return;
  }

  if (cmd === 'login-by-code') {
    const code = String(args.code || '').trim();
    if (!code) {
      output({ ok: false, error: 'missing_code', message: '--code is required' });
      process.exitCode = 2;
      return;
    }
    const login = await callPassportApi(
      'signInByCode',
      { ...baseParam, code, code_type: baseParam.code_type, scene: baseParam.scene },
      signer,
      apiMap
    );
    const payload = {
      ok: true,
      phone,
      result: login,
    };
    if (login.json && Number(login.json.errno) === 0 && login.json.ticket) {
      payload.sign_auth = buildSignAuth(login.json.ticket, args);
    }
    output(payload);
    return;
  }

  if (cmd === 'get-captcha') {
    const result = await callPassportApi('getCaptcha', baseParam, signer, apiMap);
    output({ ok: true, phone, result });
    return;
  }

  if (cmd === 'verify-captcha') {
    const captchaCode = String(args.captcha_code || '').trim();
    if (!captchaCode) {
      output({ ok: false, error: 'missing_captcha_code', message: '--captcha_code is required' });
      process.exitCode = 2;
      return;
    }
    const result = await callPassportApi('verifyCaptcha', { ...baseParam, captcha_code: captchaCode }, signer, apiMap);
    output({ ok: true, phone, result });
  }
}

main().catch((err) => {
  output({ ok: false, error: 'exception', message: err && err.message ? err.message : String(err) });
  process.exitCode = 1;
});
