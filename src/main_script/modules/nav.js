function getCourseTree() {
    const courseTree = [];
    const treeDiv = document.getElementById(COURSE_TREE_ID);
    if (!treeDiv) {
        console.warn(`未找到id为${COURSE_TREE_ID}的div`);
        return courseTree;
    }
    const nodes = treeDiv.querySelectorAll(COURSE_TREE_NODE_FEATURE_CLASS);
    nodes.forEach(node => {
        courseTree.push(node);
    });

    return courseTree;
}

function findCourseTree() {
    courseTree = getCourseTree();
    if (courseTree.length === 0) {
        console.error('未找到课程树, 请检查页面结构或联系作者');
    }
}

function nodeType(node) {
    const span = node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
    if (!span) {
        console.warn('未找到span.posCatalog_name');
        const titleSpan = node.querySelector(COURSE_TREE_NODE_TITLE_FEATURE_CLASS);
        if (titleSpan) {
            console.log('使用span.posCatalog_title作为标题');
            return 'Title';
        }
        return 'Unknown';
    } else {
        if (span.onclick == null) {
            return 'Block';

        } else {
            const pending = node.querySelector('.orangeNew'); 
            if (pending) {
                return 'Pending';
            } else {
                return 'Finished';
            }
        }
    }
}

function nextCourse() {
    if (courseTreeIndex < courseTree.length) {
        return courseTree[courseTreeIndex++];
    } else {
        return null; 
    }
}

function initializeTreeIndex() {
    let node;
    courseTreeIndex = 0;
    while(node = nextCourse()) {
        if(node.classList.contains(COURSE_TREE_NODE_CURRENT_FEATURE_CLASS)) {
            console.log('已找到当前激活的课程节点:', node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS).title);
            courseTreeIndex--;
            return node.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS).title;
        } 
    }
    console.error('初始化错误, 未找到激活的课程节点');
}

function timeSleep(time) {
    time = time + Math.floor(Math.random() * 50);
    return new Promise(resolve => setTimeout(resolve, time));
}

function waitForElement(getter, callback, interval = DEFAULT_INTERVAL_TIME, maxTry = DEFAULT_TRY_COUNT) {
    let tryCount = 0;
    let stopped = false;
    function tryFind() {
        if (stopped) return;
        let el = null;
        try {
            el = getter();
        } catch (e) {
            // 捕获 DeadObject 或跨域等异常
            console.warn('[waitForElement] getter 异常，终止本轮检测', e);
            stopped = true;
            callback(null);
            return;
        }
        if (el) {
            callback(el);
        } else if (tryCount < maxTry) {
            tryCount++;
            setTimeout(tryFind, interval);
        } else {
            callback(null);
        }
    }
    tryFind();
    // 返回一个停止函数，供外部取消
    return () => { stopped = true; };
}

function continueToNextChapter() {
    if (nextLock || nextCooldown) {
        console.log('[锁] 跳转冷却中，跳过本次 continueToNextChapter');
        return;
    }
    nextLock = true;
    nextCooldown = true; // 进入冷却

    // ...原有跳转逻辑...

    // 跳转后冷却，比如5秒
    setTimeout(() => {
        nextCooldown = false;
        console.log('章节跳转冷却结束');
    }, 10 * DEFAULT_SLEEP_TIME); 

    const nextBtn = document.getElementById(NEXTBTN_ID);

    if (nextBtn) {
        if (nextBtn.style.display === 'none') {
            confirm('课程已完成');
            allTaskDown = true;
            nextLock = false;
            return;
        }
    } else {
        nextLock = false;
        throw new Error('元素缺失, 已终止');
    }

    findCourseTree(); //由于此时课程树有元素变化（主要是COURSE_TREE_NODE_CURRENT_FEATURE_CLASS），需要刷新
    let currentTitle = initializeTreeIndex();
    let nextCourseNode = nextCourse();
    let skippedCount = 0;
    while(nodeType(nextCourseNode) !== 'Unknown' && nodeType(nextCourseNode) !== 'Pending') {
        const nameSpan = nextCourseNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
        const titleSpan = nextCourseNode.querySelector(COURSE_TREE_NODE_TITLE_FEATURE_CLASS);
        const title = nameSpan?.title ?? titleSpan?.title ?? '未知标题';
        console.log('跳过已完成和锁定课程/目录:', title);
        nextCourseNode = nextCourse();
        if(!nextCourseNode) {
            break;
        }
        skippedCount++;
    }
    if (nextCourseNode) {
        let nextChapter = nextCourseNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS);
        console.log('正在跳转到下一课程:', nextChapter.title);
        if (nextChapter) {
            if (currentTitle === nextChapter.title) {
                let aimNode = nextCourse();
                console.log('当前章节已激活，跳过');
                while(nodeType(aimNode) !== 'Unknown' && nodeType(aimNode) !== 'Pending') {
                    console.log('执行章节跳转循环中...')
                    aimNode = nextCourse();
                    if(!aimNode) {
                        confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
                        allTaskDown = true;
                        nextLock = false; 
                        return;
                    }
                    skippedCount++; 
                }
                nextChapter = aimNode.querySelector(COURSE_TREE_NODE_INTERACT_FEATURE_CLASS); 
                console.log('循环执行完毕，正在跳转到下一课程:', nextChapter.title);           
            }  
            if (nextChapter) {
                timeSleep(DEFAULT_SLEEP_TIME).then(() => { 
                    console.log('即将跳转到下一章节');
                    nextChapter.click();
                    console.log('已点击章节:', nextChapter.title);
                    nextLock = false; 
                });
            } else {
                confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
                allTaskDown = true;
                nextLock = false; 
            }
        } else {
            confirm('课程已完成');
            allTaskDown = true;
            nextLock = false; 
        }
    } else {
        confirm('未找到下一个课程节点, 可能是课程已全部完成或结构异常,脚本已退出');
        allTaskDown = true;
        nextLock = false; 
    }
}

function findOuterDoc() {
    const outerIframe = document.getElementById(OUTER_IFRAME_ID);
        if (!outerIframe) return null;
        let outerDoc;
        try {
            outerDoc = outerIframe.contentDocument || outerIframe.contentWindow.document;
        } catch (e) {
            console.warn('跨域, 无法访问iframe内容');
            return null;
        }
        if (!outerDoc) {
            console.log('[调试] 未找到 outerDoc');
            return null;
        }
        if (outerDoc.location.href === IFRAME_LOADING_URL) {
            console.log('[调试] outerDoc 仍为 about:blank,等待加载');
            return null;
        }
        console.log('已找到 outerDoc:', outerDoc);
        return outerDoc;
}

function findInnerDocs(outerDoc) {
    const innerIframes = Array.from(outerDoc.querySelectorAll('iframe')).filter(
        iframe =>
            iframe.classList?.contains(INNER_COURSE_IFRAME_FEATURE_CLASS) ||
            iframe.src?.includes('ananas/modules/work')       // 满足 src 包含特定路径
    );
    const result = [];
    console.log('开始核对');
    const needSkip = outerDoc.querySelectorAll('.ans-job-icon');
    if (needSkip?.length > 1 && innerIframes.length < needSkip.length) {
        console.warn('检测到测验题目数量小于课程内实际测验题目数量不符，将重新回调', needSkip.length, innerIframes.length);
        return null;
    }
    innerIframes.forEach(innerIframe => {
        let Type = '';
        let innerDoc;

        // 判断 iframe 类型
        if (innerIframe.classList.contains(VIDEO_IFRAME_FEATURE_CLASS)) {
            Type = 'Video';
        } else if (innerIframe.classList.contains(PDF_DOC_FEATURE_CLASS)) {
            Type = 'Pdf';
        } else if (innerIframe.src?.includes('/ananas/modules/work/')) {
            Type = 'Work';
        } else {
            Type = 'Unknown';
        }

        // 获取 innerDoc
        try {
            innerDoc = innerIframe.contentDocument || innerIframe.contentWindow.document;
            if (!innerDoc) {
                console.log('[调试] 未找到 innerDoc');
                throw new Error('innerDoc 未找到'); // 抛出异常，跳转到 catch
            }

            if (innerDoc.location.href === IFRAME_LOADING_URL) {
                console.log('[调试] innerDoc 仍为 about:blank, 等待加载');
                throw new Error('innerDoc 加载中'); 
            }
        } catch (e) {
            console.warn('[备用] 跨域, 无法访问 iframe 内容');
            return null;
        }
        result.push({ innerDoc, Type });
    });
    if (result.length === 0) {
        console.log('[调试] 尝试检测测验题目');
        // 备用手段：尝试查找 src 包含 /ananas/modules/work/ 的 iframe
        const workIframe = Array.from(outerDoc.querySelectorAll('iframe')).find(
            iframe => iframe.src?.includes('/ananas/modules/work/')
        );
        if (workIframe) {
            try {
                let workDoc;
                try {
                    workDoc = workIframe.contentDocument || workIframe.contentWindow.document;
                } catch (e) {
                    console.warn('[备用] 获取 workDoc 失败', e);
                    return null;
                }
                console.log('[备用] workDoc:', workDoc);
                if (!workDoc) {
                    console.warn('[备用] workDoc 为 null');
                    return null;
                } else if (workDoc.location.href === IFRAME_LOADING_URL) {
                    console.warn('[备用] workDoc 仍为 about:blank');
                    return null;
                } else {
                    console.log('[备用] 通过 src 查找到了 work iframe innerDoc');
                    result.push({ innerDoc: workDoc, Type: 'Work' });
                }
            } catch (e) {
                console.warn('[备用] 跨域, 无法访问 work iframe 内容');
                return null;
            }
        } else {
            console.log('[备用] 未找到 work iframe');
            return null;
        }
        
    }
    console.log('再次核对');
    if (needSkip?.length > 1 && result.length < needSkip.length) {
        console.warn('检测到测验题目数量小于课程内实际测验题目数量不符，将重新回调');
        return null;
    }
    return result;
}
