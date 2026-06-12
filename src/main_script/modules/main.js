async function handleIframeChange(prama = DEFAULT_TEST_OPTION) { 
    if (allTaskDown) return;


    if (handleIframeLock) {
        console.log('handleIframeChange 已加锁，跳过本次调用');
        return;
    }
    handleIframeLock = true;

    // 唯一性控制，防止异步出bug（事实上确实会出很多bug）
    let firstLayerCancel = null;
    let secondLayerCancel = null;
    let thirdLayerCancel = null;
    let FourthLayerCancel = null;

    let learningFix = false;

    (function firstLayer() {  //抓取三层iframe
        if (firstLayerCancel) firstLayerCancel();
        firstLayerCancel = waitForElement(
            () => {
                if (allTaskDown) return;
                console.log('第一层回调执行');
                let outerDoc = findOuterDoc();
                const learning2 = document.getElementById('dct2');
                const learning3 = document.getElementById('dct3');
                if (learning3 && prama === 3 && !learningFix) {
                    console.log('检测到特殊页面结构，即将跳转');
                    learning2.click();
                    learningFix = true;
                    return null;
                }
                return outerDoc;
            },
            (outerDoc) => {
                // 第二层
                (function secondLayer() {
                    if (secondLayerCancel) secondLayerCancel();
                    secondLayerCancel = waitForElement(
                        () => {
                            if (allTaskDown) return;
                            console.log('第二层回调执行');
                            let innerDoc = findInnerDocs(outerDoc);
                            return innerDoc;
                        },
                        (InnerDocs = []) => {
                        (async function thirdLayer() {
                            if (!Array.isArray(InnerDocs) || InnerDocs.length === 0) {
                                console.warn('内层Docs为空，尝试跳过');
                                console.log('开始检测特殊页面结构');
                                console.log('检查是否有学习测验');
                                await timeSleep(10 * DEFAULT_SLEEP_TIME);
                                let learningTest = document.getElementById('dct2');
                                const learningTestFix = document.getElementById('dct3');
                                if (learningTestFix) {
                                    learningTest = learningTestFix;
                                }
                                if (learningTest && (prama === 1 || prama === 3) && !hasEnterdct2) {
                                    const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');
                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                        learningTest.click();
                                        hasEnterdct2 = true;
                                        await timeSleep(DEFAULT_SLEEP_TIME);
                                        handleIframeLock = false; //
                                        await handleIframeChange(1);  
                                    }   
                                    return;
                                } else {
                                    console.log('此章节学习测验已处理');
                                    if (prama !== 2) answerTable = [];
                                    console.log('已处理完所有章节任务，准备跳转到下一章节');
                                    if (DEFAULT_TEST_OPTION !== 0) await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                    const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');

                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                        hasEnterdct2 = false;
                                        continueToNextChapter();
                                    }
                                    
                                }
                                return;
                            }
                            // 第三层
                            console.log('第三层回调执行');
                            console.log('找到的内层文档数目:', InnerDocs.length);
                            const needSkip = outerDoc.querySelectorAll('.ans-job-icon');
                            let taskCount = 0;
                            async function runTasksSerially() {
                                for (const { innerDoc, Type } of InnerDocs) { // for...of 防错乱
                                    console.log(`处理 ${Type} 任务点...`);
                                    try {    
                                        if (taskCount >= needSkip.length) {
                                            console.log('已处理完所有任务点，准备跳转到下一章节');
                                            if (Type === 'Work') prama = 0; 
                                        } else if (needSkip[taskCount].getAttribute('aria-label') === '任务点已完成') {
                                            console.log('任务点已完成，跳过');
                                            if (Type === 'Work') prama = 0; 
                                        } else if (Type === 'Video') {
                                            console.log('该章节为VIDEO,进行参数捕获');
                                            await new Promise((resolve) => {
                                                if (FourthLayerCancel) FourthLayerCancel();
                                                FourthLayerCancel = waitForElement(
                                                    () => {
                                                        if (allTaskDown) return;
                                                        console.log('第四层回调执行');
                                                        return findVideoElement(innerDoc);
                                                    },
                                                    async (innerParam) => {
                                                        if (!innerParam) {
                                                            console.warn('页面异常加载，尝试跳过');
                                                            resolve();
                                                            return;
                                                        }
                                                        const { videoDiv, launchBtn, target, playControlBtn, paceList , muteBtn } = innerParam;
                                                        await autoPlayVideo(
                                                            innerDoc,
                                                            videoDiv,
                                                            launchBtn,
                                                            target,
                                                            playControlBtn,
                                                            paceList,
                                                            muteBtn
                                                        );
                                                        resolve();
                                                    }
                                                );
                                            });
                                        } else if (Type === 'Pdf') {
                                            console.log('该章节为PDF,进行参数捕获');
                                            await new Promise((resolve) => {
                                                if (thirdLayerCancel) thirdLayerCancel();
                                                thirdLayerCancel = waitForElement(
                                                    () => {
                                                        return findPdfElement(innerDoc);
                                                    },
                                                    async ({ pdfHtml } = {}) => {
                                                        if (!pdfHtml) {
                                                            console.error('请求超时, 请检查网络或与作者联系');
                                                            resolve();
                                                            return;
                                                        }
                                                        const toBottom = await scrollPdfToBottom(pdfHtml);
                                                        if (toBottom) {
                                                            console.log('PDF滚动成功！');
                                                        } else {
                                                            console.warn('PDF多次滚动无效，可能页面未加载完全');
                                                        }
                                                        await timeSleep(2 * DEFAULT_SLEEP_TIME);
                                                        console.log('章节处理完毕');
                                                        resolve();
                                                    }
                                                );
                                            });
                                        } else if (Type === 'Work') {
                                            console.log('该章节为WORK,进行参数捕获');
                                            await new Promise((resolve) => {
                                                if (thirdLayerCancel) thirdLayerCancel();
                                                thirdLayerCancel = waitForElement(
                                                    () => {
                                                        return findWorkElement(innerDoc);
                                                    },
                                                    async ({ testDoc, testList, submitBtn } = {}) => {
                                                        if (!testList || testList.length === 0) {
                                                            console.error('请求超时, 请检查网络或与作者联系');
                                                            resolve();
                                                            return;
                                                        }
                                                        console.log('已找到测试题目:', testList);
                                                        if (prama === 2) {
                                                            console.warn('检测为不及格，开始修补模式');
                                                            const answerBasicList = testDoc.querySelectorAll('.newAnswerBx');
                                                            if (answerBasicList.length === 0) {
                                                                console.warn('未找到答案列表，可能是页面加载异常');
                                                                resolve();
                                                                return;
                                                            }
                                                            let index = 0;
                                                            let answerHistory = [];
                                                            for (const answerBasic of answerBasicList) {
                                                                index++;
                                                                if (!answerHistory[index]) {
                                                                    answerHistory[index] = [];
                                                                }
                                                                const answerCon = answerBasic.querySelector('.answerCon');
                                                                let answerMark;
                                                                const wrong = answerBasic.querySelector('.marking_cuo');
                                                                const half = answerBasic.querySelector('.marking_bandui');
                                                                if (wrong) {
                                                                    answerMark = 'wrong';
                                                                } else if (half) {
                                                                    answerMark = 'half';
                                                                } else {
                                                                    answerMark = 'right';
                                                                }
                                                                answerHistory[index].push({
                                                                    answer: answerCon.textContent.trim(),
                                                                    mark: answerMark
                                                                });
                                                            }
                                                            console.log('已获取到答案历史:', answerHistory);
                                                            //confirm('[调试],已获取到答案历史，准备修补');
                                                            let answerJson = answerFixes(testList, answerHistory);
                                                            if (answerJson.length === 0) {
                                                                confirm('fix答案失败');
                                                                resolve();
                                                                return;
                                                            } else {
                                                                autoFillAnswers(testList, answerJson);
                                                                console.log('已自动填充答案');
                                                                resolve();
                                                            }
                                                            //confirm('已修补答案，准备提交');
                                                            submitBtn.click();
                                                            await timeSleep(DEFAULT_SLEEP_TIME);
                                                            const configElement = document.getElementById('workpop');
                                                            const configBtn = document.getElementById('popok');
                                                            if (configElement && window.getComputedStyle(configElement).display !== 'none') {
                                                                if (configBtn) {
                                                                    configBtn.click();
                                                                    console.log('已自动点击确定按钮');
                                                                } else {
                                                                    console.warn('未找到确定按钮');
                                                                }
                                                            }
                                                            await timeSleep(2 * DEFAULT_SLEEP_TIME);
                                                            //confirm ('已提交测试题目，等待结果');
                                                            const configContent = document.getElementById('popcontent');
                                                            if (configContent && configContent.textContent.includes('未达到及格线')) {
                                                                console.warn('检测到未及格，需重做！');
                                                                configBtn.click();
                                                                await timeSleep(DEFAULT_SLEEP_TIME);
                                                                handleIframeLock = false; //
                                                                await handleIframeChange(2); 
                                                                return;
                                                            } else {
                                                                console.log('已成功提交测试题目');
                                                                answerTable = [];
                                                                console.log('已处理完所有章节任务，准备跳转到下一章节');
                                                                await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                                                const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                                                if (unfinished) {
                                                                    // 存在未完成任务点
                                                                    console.log('有未完成的任务点');
                                                                } else {
                                                                    // 没有未完成任务点
                                                                    console.log('所有任务点已完成');
                                                                    hasEnterdct2 = false;
                                                                    continueToNextChapter();
                                                                }
                                                                
                                                            }
                                                        } else if (window._uxWs && window._uxWs.readyState === WebSocket.OPEN) {
                                                            console.log('已找到题目，开始传输');
                                                            if (answerTable) answerTable = [];
                                                            const fontBase64 = (typeof getFontBase64 === 'function') ? getFontBase64() : '';
                                                            const quizPayload = (typeof extractQuizData === 'function') ? extractQuizData(testDoc) : { questions: [], images: [] };
                                                            const msg = {
                                                                type: 'quizData',
                                                                fontBase64: fontBase64,
                                                                questions: quizPayload.questions,
                                                                images: quizPayload.images
                                                            };
                                                             window._uxWs.send(JSON.stringify(msg));
                                                            await new Promise(resolve => {
                                                                function onMessage(event) {
                                                                    try {
                                                                        // 判断是否收到的是答案json（一般不是"收到"而是json字符串）
                                                                        let answerJson;
                                                                        try {
                                                                            answerJson = JSON.parse(event.data);
                                                                        } catch (e) {
                                                                            // 不是json就忽略
                                                                            if (event.data === '收到') {
                                                                                window._uxWs.removeEventListener('message', onMessage);
                                                                                console.log('收到Python回信，继续后续流程');
                                                                                resolve();
                                                                            }
                                                                            return;
                                                                        }
                                                                        // 如果能解析为json，自动填答
                                                                        autoFillAnswers(testList, answerJson);
                                                                        window._uxWs.removeEventListener('message', onMessage);
                                                                        console.log('已自动填充答案');
                                                                        resolve();
                                                                    } catch (e) {
                                                                        console.warn('处理回信时出错', e);
                                                                    }
                                                                }
                                                                window._uxWs.addEventListener('message', onMessage);
                                                            });
                                                            //confirm('已创建答案，准备提交');
                                                            submitBtn.click();
                                                            await timeSleep(DEFAULT_SLEEP_TIME);
                                                            const configElement = document.getElementById('workpop');
                                                            const configBtn = document.getElementById('popok');
                                                            if (configElement && window.getComputedStyle(configElement).display !== 'none') {
                                                                if (configBtn) {
                                                                    configBtn.click();
                                                                    console.log('已自动点击确定按钮');
                                                                } else {
                                                                    console.warn('未找到确定按钮');
                                                                }
                                                            }
                                                            await timeSleep(2 * DEFAULT_SLEEP_TIME);
                                                            const configContent = document.getElementById('popcontent');
                                                            if (configContent && configContent.textContent.includes('未达到及格线')) {
                                                                configBtn.click();
                                                                await timeSleep(DEFAULT_SLEEP_TIME);
                                                                console.warn('检测到未及格，需重做！');
                                                                handleIframeLock = false; 
                                                                await handleIframeChange(2); 
                                                                return;
                                                            } else {
                                                                console.log('已成功提交测试题目');
                                                                answerTable = [];
                                                                console.log('已处理完所有章节任务，准备跳转到下一章节');
                                                                await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                                                const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                                                if (unfinished) {
                                                                    // 存在未完成任务点
                                                                    console.log('有未完成的任务点');
                                                                } else {
                                                                    // 没有未完成任务点
                                                                    console.log('所有任务点已完成');
                                                                    hasEnterdct2 = false;
                                                                    continueToNextChapter();
                                                                }
                                                                                                                            
                                                            }
                                                            
                                                        } else {
                                                            console.warn('WebSocket未连接，无法发送测试题目');
                                                        }

                                                    }
                                                );
                                            });
                                            
                                        }
                                    } finally {
                                        console.log(`任务点 ${taskCount + 1} / ${needSkip.length} 已处理`);
                                        taskCount++;
                                    }
                                }
                                // 所有任务完成后
                                console.log('所有章节任务已完成，准备跳转到下一章节');
                                console.log('检查是否有学习测验');
                                await timeSleep(10 * DEFAULT_SLEEP_TIME);
                                let learningTest = document.getElementById('dct2');
                                const learningTestFix = document.getElementById('dct3');
                                if (learningTestFix) {
                                    learningTest = learningTestFix;
                                }
                                if (learningTest && (prama === 1 || prama === 3) && !hasEnterdct2) {
                                    const unfinished = document.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.warn('有未完成的任务点,尝试跳过');
                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                         
                                    }
                                    learningTest.click();
                                    hasEnterdct2 = true;
                                    await timeSleep(DEFAULT_SLEEP_TIME);
                                    handleIframeLock = false; //
                                    await handleIframeChange(1);                                
                                } else {
                                    console.log('此章节学习测验已处理');
                                    if (prama !== 2) answerTable = [];
                                    console.log('已处理完所有章节任务，准备跳转到下一章节');
                                    if (DEFAULT_TEST_OPTION !== 0) await timeSleep(25 * DEFAULT_SLEEP_TIME);
                                    const unfinished = outerDoc.querySelector('.ans-job-icon[aria-label="任务点未完成"]');
                                    if (unfinished) {
                                        // 存在未完成任务点
                                        console.log('有未完成的任务点');
                                    } else {
                                        // 没有未完成任务点
                                        console.log('所有任务点已完成');
                                    
                                    }
                                    hasEnterdct2 = false;   
                                    continueToNextChapter();   
                                }
                            }

                            // 调用
                            runTasksSerially();
                        })();
                    }
                    );
                })();
            }
        );
    })();
}

function startScriptWithMask(mainFunc) { // 启动脚本并创建遮罩，因为只有用户主动激活主页面脚本才能正常运行
    // 创建全屏透明遮罩
    const mask = document.createElement('div');
    mask.style.position = 'fixed';
    mask.style.left = 0;
    mask.style.top = 0;
    mask.style.width = '100vw';
    mask.style.height = '100vh';
    mask.style.zIndex = 99999;
    mask.style.background = 'rgba(0,0,0,0)';
    mask.style.cursor = 'pointer';
    mask.title = '启动器';
    document.body.appendChild(mask);

    confirm('本脚本仅供学习交流使用, 请遵守相关法律法规。\n\n请先关闭浏览器的开发者工具, 点击确定后单击页面任意处以运行脚本。\n\n如果想停止脚本, 随时刷新页面即可。');

    mask.addEventListener('click', function () { 
        document.body.removeChild(mask);
        mainFunc();
    });
}

function main() {
    console.log('[uX] 脚本已启动, 开始刷课...');
    if (typeof checkPageContext === 'function') checkPageContext();
    if (typeof startChapterObserver === 'function') startChapterObserver();
    // 通知 Python 页面已加载
    try {
        if (window._uxWs && window._uxWs.readyState === WebSocket.OPEN) {
            window._uxWs.send(JSON.stringify({
                type: "pageReady",
                url: location.href,
                title: document.title
            }));
        }
    } catch(e) {}
    
    const leftEl = document.querySelector(IFRAME_MAIN_FEATURE_CLASS);
    if (leftEl) {
        const leftObserver = new MutationObserver(() => {
            skipSign++;
            if(skipSign % 2 === 0) {
                handleIframeLock = false; // 每次检测到变动后解锁
                handleIframeChange(3); 
            }
        });
        leftObserver.observe(leftEl, { childList: true, subtree: true });
        handleIframeChange(3);
    } else {
        console.error('未找到 class 为 lefaramt 的元素');
    }
}

Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });
Object.defineProperty(document, 'hidden', { get: () => false });

document.addEventListener('visibilitychange', function(e) {
    e.stopImmediatePropagation();
}, true);

window.onblur = null;
window.onfocus = null;
window.addEventListener = new Proxy(window.addEventListener, {
    apply(target, thisArg, args) {
        if (['blur', 'focus'].includes(args[0])) return;
        return Reflect.apply(target, thisArg, args);
    }
});

findCourseTree(); // 初始化课程树
initializeTreeIndex();

if (DEFAULT_SPEED_OPTION) {
    console.log('强制速度模式已开启,目前倍速为:', DEFAULT_SPEED);  
} else {
    console.log('未开启强制速度模式');
}

// 启动入口
startScriptWithMask(main);
