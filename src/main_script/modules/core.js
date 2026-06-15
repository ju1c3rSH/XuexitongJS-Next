/**使用说明：
 * uXueXiTongX 学习通一键全自动刷课脚本
 * 
 * 功能简介：
 * - 自动识别课程树结构，自动切换章节
 * - 自动播放视频、自动回答互动题目、自动切换倍速
 * - 自动检测 PDF 文档并自动翻页
 * - 2nm的容错处理
 * 
 * 注意事项：
 * - 目前单一章节只识别第一个视频/PDF元素，可能会漏刷
 * - 仅支持学习通网页版，目前仅在FireFox验证，理论上不同浏览器均兼容（IE除外）（真有人用IE？？）
 * - 对于非视频/PDF类型的课程，脚本会尝试直接跳过
 * - 欢迎Issue反馈bug或建议，但请一定一定给出详细信息
 * 
 * 使用说明：
 * 1. 仅在学习通平台页面使用，具体用法参见README.md。
 * 2. 启动脚本后，需手动点击页面以激活脚本。
 * 3. 如需停止，刷新页面即可。
 * 4. 请勿用于商业用途或违反相关法律法规。（这坨玩意有人商用？？？）
 * 
 * 作者：unraous
 * 邮箱：unraous@qq.com
 * 日期：2025-06-16
 * 版本：v1.2.2
 */


const DEFAULT_TEST_OPTION = globalThis.LAUNCH_OPTION ?? 0;
const DEFAULT_SPEED_OPTION = globalThis.FORCE_SPEED ?? false;
const DEFAULT_SPEED = globalThis.SPEED ?? 2;

console.log('测试选项:', DEFAULT_TEST_OPTION);
console.log('强制倍速选项:', DEFAULT_SPEED_OPTION);
console.log('默认倍速:', DEFAULT_SPEED);

const POLL_INTERVAL_MS = globalThis.POLL_INTERVAL_MS ?? 100;
const DEFAULT_SLEEP_TIME = Math.floor(POLL_INTERVAL_MS * 4 + Math.random() * POLL_INTERVAL_MS * 2); // 默认延迟 = poll_interval_ms*4 ± 50%
const DEFAULT_INTERVAL_TIME = Math.max(50, Math.floor(POLL_INTERVAL_MS * 0.85)); // 默认轮询间隔 = poll_interval_ms*0.85
const DEFAULT_TRY_COUNT = globalThis.POLL_MAX_RETRY ?? 50; // 默认最大尝试次数50次

const COURSE_TREE_ID = 'coursetree'; 
const COURSE_TREE_NODE_FEATURE_CLASS = 'div.posCatalog_select';
const COURSE_TREE_NODE_TITLE_FEATURE_CLASS = 'span.posCatalog_title';
const COURSE_TREE_NODE_CURRENT_FEATURE_CLASS = 'posCatalog_active';
const COURSE_TREE_NODE_INTERACT_FEATURE_CLASS = 'span.posCatalog_name';
const COURSE_TREE_NODE_UNFINISHED_FEATURE_CLASS = '.jobUnfinishCount';

const VIDEO_IFRAME_ID = 'video';
const VIDEO_QUESTION_ID = 'ext-comp-1046'; 
const VIDEO_QUESTION_COMPLETE_ID = 'videoquiz-continue';
const VIDEO_QUESTION_SUBMITTING_ID = 'videoquiz-submitting';
const VIDEO_PLAY_FEATURE_CLASS = '.vjs-play-control';
const VIDEO_ENDED_FEATURE_CLASS = 'vjs-ended';
const VIDEO_IFRAME_FEATURE_CLASS = 'ans-insertvideo-online';
const VIDEO_LAUNCH_FEATURE_CLASS = '.vjs-big-play-button';
const VIDEO_PAUSED_FEATURE_CLASS = 'vjs-paused';
const VIDEO_MUTEBTN_FEATURE_CLASS = '.vjs-mute-control';
const VIDEO_PACELIST_FEATURE_CLASS = 'li.vjs-menu-item';
const VIDEO_HAS_LAUNCHED_FEATURE_CLASS = 'vjs-has-started';
const VIDEO_PACE_SELECTED_FEATURE_CLASS = 'vjs-menu-item-selected';
const VIDEO_QUESTION_SUBMIT_FEATURE_CLASS = '.ans-videoquiz-submit';
const VIDEO_QUESTION_RADIOS_FEATURE_CLASSES = '.tkItem_ul .ans-videoquiz-opt input[type="radio"]';
const VIDEO_QUESTION_CHECKBOXES_FEATURE_CLASSES = '.tkItem_ul .ans-videoquiz-opt input[type="checkbox"]';

const PDF_IFRAME_ID = 'panView';
const PDF_DOC_FEATURE_CLASS = 'insertdoc-online-pdf';

const IFRAME_LOADING_URL= 'about:blank';
const NEXTBTN_ID = 'prevNextFocusNext';
const OUTER_IFRAME_ID = 'iframe'; 
const INNER_COURSE_IFRAME_ID = 'iframe.ans-attach-online';
const INNER_COURSE_IFRAME_FEATURE_CLASS = 'ans-attach-online';
const IFRAME_MAIN_FEATURE_CLASS = '.content'; // 适配左右目录布局




var allTaskDown = false; 
var courseTree = [];
var courseTreeIndex = 0;
var nextLock = false; 
var skipSign = 0;
var answerTable = []; 
var handleIframeLock = false;
var nextCooldown = false;
var videoLock = false; // 视频锁，防止多次点击播放按钮
var hasEnterdct2 = false; // 临时补丁，防止多次进入测验题目处理流程

// 常驻 WebSocket 连接，天活检测标志
window._uxAlive = true;
window._uxWs = null;

function connectWebSocket() {
    if (window._uxWs && window._uxWs.readyState === WebSocket.OPEN) return;
    if (window._uxWs && window._uxWs.readyState === WebSocket.CONNECTING) return;
    try {
        window._uxWs = new WebSocket("ws://localhost:8765");
        window._uxWs.onopen = function() {
            console.log("[uX] WebSocket已连接Python端口");
            window._uxAlive = true;
        };
        window._uxWs.onerror = function(e) {
            console.warn("[uX] WebSocket连接失败", e);
        };
        window._uxWs.onclose = function() {
            console.warn("[uX] WebSocket已关闭，3秒后重连");
            window._uxWs = null;
            setTimeout(connectWebSocket, 3000);
        };
    } catch (e) {
        console.warn("[uX] WebSocket创建失败", e);
        setTimeout(connectWebSocket, 3000);
    }
}
connectWebSocket();


var _uxLastChapterText = '';

function sendConfigUpdate(data) {
    if (window._uxWs && window._uxWs.readyState === WebSocket.OPEN) {
        window._uxWs.send(JSON.stringify({
            type: 'configSync',
            payload: data
        }));
    }
}

function checkPageContext() {
    const url = location.href;
    if (url.includes('courseid=')) {
        sendConfigUpdate({
            currentUrl: url,
            historyUrl: url,
        });
    }
}

function startChapterObserver() {
    const tree = document.getElementById('coursetree');
    if (!tree) return;
    new MutationObserver(function() {
        const active = tree.querySelector('.posCatalog_active .posCatalog_name');
        if (active && active.textContent.trim() !== _uxLastChapterText) {
            _uxLastChapterText = active.textContent.trim();
            sendConfigUpdate({
                chapterTitle: _uxLastChapterText,
                currentUrl: location.href,
                historyUrl: location.href,
            });
        }
    }).observe(tree, { childList: true, subtree: true, characterData: true });
}
