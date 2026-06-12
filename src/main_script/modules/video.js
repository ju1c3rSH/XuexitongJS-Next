function muteVideo (muteBtn) {
    if (muteBtn) {
    if (muteBtn.title === '取消静音') {
        console.log('已是静音状态，跳过');
    } else if (muteBtn.title === '静音') {
        muteBtn.click();
        console.log('已自动点击静音按钮');
    } else {
        console.warn('静音按钮的title未知:', muteBtn.title);
    }
} else {
    console.warn('未找到静音按钮元素');
}
}

function selectMenuItem(paceList) {
    // 2x > 1.5x > 1.25x
    const targets = ["2x", "1.5x", "1.25x"];
    let found = null;
    for (const speed of targets) {
        found = Array.from(paceList).find(li => li.textContent.includes(speed));
        if (found) break;
    }
    if (found) {
        found.click();
        timeSleep(DEFAULT_SLEEP_TIME).then(() => {
            if (found.classList.contains(VIDEO_PACE_SELECTED_FEATURE_CLASS)) {
                console.log('已自动选择菜单项:', found);
            } else {
                console.warn('点击后未能成功选择菜单项:', found);
            }
        });
    } else {
        console.warn('未找到目标倍速菜单项');
    }
}

// 封装成函数，参数为 video 元素
function forcePlaybackRate(videoDiv, targetRate = 2.0) {
    if (!videoDiv) {
        console.warn('未找到视频元素');
        return;
    }
    const video = videoDiv.querySelector('video'); // 获取容器内的视频元素

    console.log('当前视频为：', video);
    console.log('正在强制设置视频倍速:', video.playbackRate, '->', targetRate);
    // 1. 强制设置倍速
    video.playbackRate = targetRate;
    console.log('已强制设置视频倍速:', video.playbackRate);
    // 2. 防止被检测：重写 playbackRate 属性
    Object.defineProperty(video, 'playbackRate', {
        get: function() { return targetRate; },
        set: function(val) { /* 忽略外部设置，始终保持 targetRate */ },
        configurable: true
    });

    // 3. 拦截 addEventListener，防止外部监听 playbackratechange
    var oldAddEventListener = video.addEventListener;
    video.addEventListener = function(type, listener, options) {
        if (type === 'ratechange' || type === 'playbackratechange') {
            // 不注册外部的 ratechange 监听
            return;
        }
        return oldAddEventListener.call(this, type, listener, options);
    };

    // 4. 定时修正，防止被脚本偷偷改回去
    var intervalId = setInterval(function() {
        if (video.playbackRate !== targetRate) {
            video.playbackRate = targetRate;
        }
    }, 1000);

    // 返回一个停止修正的函数
    return function stop() {
        clearInterval(intervalId);
    };
}

// 用法示例：
// const video = document.querySelector('video');
// forcePlaybackRate(video, 2.0);
// 用法：对每个 video 调用一次即可
// const stop = forcePlaybackRate(video, 2.0);

function waitForSubmitAndContinue(innerDoc) {
    return new Promise(resolve => {
        const interval = setInterval(function() {
            const submitting = innerDoc.getElementById(VIDEO_QUESTION_SUBMITTING_ID);
            if (submitting && submitting.style.display === 'none') {
                clearInterval(interval);
                // 检查“继续学习”按钮
                const contBtn = innerDoc.getElementById(VIDEO_QUESTION_COMPLETE_ID);
                if (contBtn && contBtn.style.display === 'block') {
                    contBtn.click();
                    const contInterval = setInterval(() => {
                        if (contBtn.style.display !== 'block') {
                            clearInterval(contInterval);
                            resolve(true);
                        }
                    }, 200);
                } else {
                    resolve(false);
                }
            }
        }, 200);
    });
}

function autoQuestionDeal(target, innerDoc) {
    console.log('开始处理互动题目:', target);
    videoLock = true; // 锁定视频处理，防止多次点击
    try {
        if (target) {
            let pollCount = 0;
            const maxPoll = DEFAULT_TRY_COUNT; 
            const poll = async () => {
                if (target.style.visibility === '') {
                    console.log('visi has been changed:', target.style.visibility);
                    const radios = innerDoc.querySelectorAll(VIDEO_QUESTION_RADIOS_FEATURE_CLASSES);
                    const checkboxes = innerDoc.querySelectorAll(VIDEO_QUESTION_CHECKBOXES_FEATURE_CLASSES);

                    if (checkboxes.length > 0) {
                        // 多选
                        const n = checkboxes.length;
                        for (let mask = 1; mask < (1 << n); mask++) {
                            checkboxes.forEach(cb => cb.checked = false);
                            for (let j = 0; j < n; j++) {
                                if (mask & (1 << j)) {
                                    checkboxes[j].click();
                                }
                            }
                            console.log('正在提交多选题目');
                            innerDoc.querySelector(VIDEO_QUESTION_SUBMIT_FEATURE_CLASS).click();
                            const over = await waitForSubmitAndContinue(innerDoc);
                            if (over) return;
                        }
                    } else if (radios.length > 0) {
                        // 单选
                        for (const radio of radios) {
                            radio.click();
                            console.log('正在提交单选题目');
                            innerDoc.querySelector(VIDEO_QUESTION_SUBMIT_FEATURE_CLASS).click();
                            const over = await waitForSubmitAndContinue(innerDoc);
                            if (over) return;
                        }
                    }
                } else if (pollCount < maxPoll) {
                    pollCount++;
                    setTimeout(poll, DEFAULT_SLEEP_TIME);
                }
            };
            poll();
        } else {
            console.error("没有找到目标元素");
        }
    } catch (e) {
        console.warn('autoQuestionDeal 执行异常:', e);
    }
    videoLock = false; // 解除视频处理锁
}

function findVideoElement(innerDoc) {
    const videoDiv = innerDoc.getElementById(VIDEO_IFRAME_ID); //视频主元素
    const target = innerDoc.getElementById(VIDEO_QUESTION_ID); // 互动答题元素

    const launchBtn = innerDoc.querySelector(VIDEO_LAUNCH_FEATURE_CLASS); // 视频启动按钮
    const playControlBtn = innerDoc.querySelector(VIDEO_PLAY_FEATURE_CLASS); // 视频播放按钮
    const paceList = innerDoc.querySelectorAll(VIDEO_PACELIST_FEATURE_CLASS); // 倍速播放列表
    const muteBtn = innerDoc.querySelector(VIDEO_MUTEBTN_FEATURE_CLASS); // 静音按钮

    if (!videoDiv) {
        console.log('[调试] 未找到 video 元素');
    } else {
        console.log('该章节为video,进行参数捕获', videoDiv);
        // 优化调试输出部分
        console.log('该章节为video,进行参数捕获', videoDiv);

        // 使用一个通用函数处理元素检测日志
        function logElementStatus(element, name, found = true) {
            console.log(`[调试] ${found ? '找到' : '未找到'}${name}:`, element || '');
        }

        const elementsToLog = [
            { element: launchBtn, name: '播放按钮' },
            { element: playControlBtn, name: '播放控制按钮' },
            { element: target, name: '目标元素 ext-comp-1046' },
            { element: muteBtn, name: '静音按钮' },
            { element: paceList.length > 0, name: '菜单项' }
        ];

        for (const { element, name } of elementsToLog) {
            logElementStatus(element, name, !!element);
        }

        if (paceList.length > 0) {
            console.log('[调试] 菜单项:', paceList);
        }

        if (videoDiv) {
            return { innerDoc, videoDiv, launchBtn, target, playControlBtn, paceList, muteBtn };
        }
    }  
    return null;
}

async function tryStartVideo(videoDiv, launchBtn, paceList, muteBtn) {
    let tryCount = 0;
    while (!videoDiv.classList.contains(VIDEO_HAS_LAUNCHED_FEATURE_CLASS) && tryCount < 10) {
        if (launchBtn) {
            launchBtn.click();
        } else {
            console.warn('未找到启动按钮,请用户手动点击');
            break;
        }
        tryCount++;
        await timeSleep(DEFAULT_SLEEP_TIME);
    }
    await timeSleep(DEFAULT_SLEEP_TIME);
    if (DEFAULT_SPEED_OPTION) {
        forcePlaybackRate(videoDiv, DEFAULT_SPEED)
    }
    else {
        selectMenuItem(paceList); 
    } 
    muteVideo(muteBtn);
}

function autoPlayVideo(innerDoc, videoDiv, launchBtn, target, playControlBtn, paceList, muteBtn) {
    return new Promise((resolve) => {
        if (!videoDiv) {
            console.error('请求超时,请检查网络或与作者联系');
            resolve(false);
            return;
        }
        let pauseFreeze = false;
        console.log('debug successfully');
        let observer = null;
        const checkClass = () => {
            if (videoDiv.classList.contains(VIDEO_ENDED_FEATURE_CLASS)) {
                console.log('class 已包含 vjs-ended');
                observer?.disconnect();
                resolve(true);
            } else if (!videoDiv.classList.contains(VIDEO_HAS_LAUNCHED_FEATURE_CLASS)) {       
                tryStartVideo(videoDiv, launchBtn, paceList, muteBtn);
                if (target && target.style.visibility !== 'hidden') {
                            console.log('检测为互动题目,正在处理');
                            autoQuestionDeal(target, innerDoc);
                            pauseFreeze = true;
                            setTimeout(() => {
                                pauseFreeze = false; // 5秒后解除暂停冻结
                            }, 10 * DEFAULT_SLEEP_TIME);
                }
            } else if (videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS)) {
                console.log('课程被暂停,正在检测原因');
                timeSleep(DEFAULT_SLEEP_TIME).then(() => {
                    if (videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS)) {
                        if (videoDiv.classList.contains(VIDEO_ENDED_FEATURE_CLASS)) { //由于视频结束时有暂停属性，由于延迟会产生分支跳跃到此处的情况，此步为防止一个视频循环播放
                            return;
                        }
                        if (target && target.style.visibility !== 'hidden') {
                            console.log('检测为互动题目,正在处理');
                            autoQuestionDeal(target, innerDoc);
                            pauseFreeze = true;
                            setTimeout(() => {
                                pauseFreeze = false; // 5秒后解除暂停冻结
                            }, 10 * DEFAULT_SLEEP_TIME);
                        } else if (playControlBtn) {
                            if (!pauseFreeze) {
                                console.log('未检测到互动题目,已自动点击播放按钮');
                                let tryCount = 0;
                                const maxTry = DEFAULT_TRY_COUNT - 10;
                                const tryPlay = () => {
                                    if (!videoDiv.classList.contains(VIDEO_PAUSED_FEATURE_CLASS) || tryCount >= maxTry || videoLock) {
                                        if (tryCount >= maxTry) {
                                            console.warn('多次尝试点击播放按钮未成功，请手动处理');
                                        }
                                        return;
                                    }
                                    if (!videoLock) {
                                        playControlBtn.click();
                                    }
                                    tryCount++;
                                    setTimeout(tryPlay, DEFAULT_SLEEP_TIME);
                                };
                                tryPlay();
                            } else {
                                console.warn('暂停状态已冻结,请用户手动点击播放按钮');
                            }
                             //同时兼顾后台播放功能，因为学习通只会在你鼠标离开页面时触发一次暂停，此后无检测
                        } else {
                            console.warn('未找到播放控制按钮,请用户手动点击播放');
                        }
                    } else {
                        console.log('暂停状态已自动恢复,无需处理');
                    }
                }); 
            } else if (target && target.style.visibility !== 'hidden') {
                console.log('检测为互动题目,正在处理');
                autoQuestionDeal(target, innerDoc);
                pauseFreeze = true;
                setTimeout(() => {
                    pauseFreeze = false; // 5秒后解除暂停冻结
                }, 10 * DEFAULT_SLEEP_TIME);
            } else {
                console.log('视频正在播放中，继续检测');
            } 
        };
        observer = new MutationObserver(checkClass);
        observer.observe(videoDiv, { attributes: true, attributeFilter: ['class'] });
        checkClass();
    });
}
