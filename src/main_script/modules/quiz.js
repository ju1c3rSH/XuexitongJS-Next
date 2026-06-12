function findWorkElement(innerDoc) {
    const testIframe = innerDoc.getElementById('frame_content');
    if (!testIframe) {
        console.log('[调试] 未找到 frame_content 元素');
        return null;
    }
    let testDoc;
    try {
        testDoc = testIframe.contentDocument || testIframe.contentWindow.document;
    } catch (e) {
        console.log('[调试] 获取 frame_content 的 document 失败', e);
        return null;
    }
    
    const testList = testDoc.querySelectorAll('.singleQuesId');
    if (testList.length === 0) {
        console.log('[调试] 未找到任何测试题目');
        return null;
    }
    console.log('已找到测试题目:', testList);

    const submitBtn = testDoc.querySelector('.btnSubmit');
    if (!submitBtn) {
        console.log('[调试] 未找到提交按钮');
        return null;
    }
    return { testDoc, testList , submitBtn };
}

function autoFillAnswers(testList, answerJson) {
    answerJson.forEach(item => {
        const qNum = item["question_id"];
        const ans = item["answer"];
        for (const quesDiv of testList) {
            const iTag = quesDiv.querySelector('i');
            if (iTag && iTag.textContent.trim() === qNum) {
                // 判断题型
                const titleSpan = quesDiv.querySelector('.newZy_TItle');
                let type = '';
                if (titleSpan) {
                    const text = titleSpan.textContent.toLowerCase();
                    if (text.includes('多选') || text.includes('mul')) type = 'multi';
                    else if (text.includes('判断') || text.includes('tru')) type = 'judge';
                    else if (text.includes('单选') || text.includes('sin')) type = 'single';
                }
                // 多选题
                if (type === 'multi') {
                    // 先清除之前选中的多选项
                    const checkedSpans = quesDiv.querySelectorAll('span.check_answer_dx');
                    checkedSpans.forEach(span => span.click());

                    let ansArr = [];
                    if (typeof ans === "string") {
                        if (ans.includes(',')) {
                            ansArr = ans.split(',').map(s => s.trim());
                        } else {
                            ansArr = ans.split('').map(s => s.trim());
                        }
                    } else if (Array.isArray(ans)) {
                        ansArr = ans;
                    }
                    for (const ch of ansArr) {
                        const optSpan = quesDiv.querySelector(`span.num_option_dx[data="${ch}"]`);
                        if (optSpan) optSpan.click();
                        else console.warn(`题号${qNum}未找到选项${ch}`);
                    }
                } else if (type === 'judge') {
                    // 先清除之前选中的判断项
                    const checkedSpans = quesDiv.querySelectorAll('span.check_answer');
                    checkedSpans.forEach(span => span.click());

                    let val = ans;
                    if (val[0] === "A" || val[0] === "对" || val[0] === "t" || val[0] === "T" || val === true) val = "true";
                    else if (val[0] === "B" || val[0] === "错" || val[0] === "f" || val[0] === "F" || val === false) val = "false";
                    const optSpan = quesDiv.querySelector(`span.num_option[data="${val}"]`);
                    if (optSpan) optSpan.click();
                    else console.warn(`题号${qNum}未找到判断选项${val}`);
                } else {
                    // 单选题，先清除之前选中的
                    const checkedSpans = quesDiv.querySelectorAll('span.check_answer');
                    checkedSpans.forEach(span => span.click());

                    for (const ch of ans) {
                        const optSpan = quesDiv.querySelector(`span.num_option[data="${ch}"]`);
                        if (optSpan) optSpan.click();
                        else console.warn(`题号${qNum}未找到选项${ch}`);
                    }
                }
                break;
            }
        }
    });
}

function answerFixes(testList, answerHistory) {
    console.log('开始修补答案');
    const answerJson = []; 
    testList.forEach(quesDiv => {
        const iTag = quesDiv.querySelector('i');
        const qNum = iTag ? iTag.textContent.trim() : '';
        const qIndex = Number(qNum); // 变成数字类型
        if (!answerTable[qIndex]) {
            answerTable[qIndex] = [];
        }
        const titleSpan = quesDiv.querySelector('.newZy_TItle');
        let type = '';
        if (titleSpan) {
            if (titleSpan.textContent.includes('多选')) type = 'multi';
            else if (titleSpan.textContent.includes('判断')) type = 'judge';
            else if (titleSpan.textContent.includes('单选')) type = 'single';
        }

        if (type === 'multi') { // 多选题
            const options = quesDiv.querySelectorAll('span.num_option_dx');
            console.log('多选题修补之初的table:', answerTable);
            if (answerTable[qIndex].length === 0) {
                console.log('进入初始化')
                answerTable[qIndex] = Array(options.length).fill(-1);
            }
            
            if (answerHistory[qIndex]?.some(record => record.mark === 'right')) {
                answerJson.push({
                    "题号": qNum,
                    "答案": answerHistory[qIndex][0]?.answer || ""
                });
                return;
            } else if (answerHistory[qIndex]?.some(record => record.mark === 'half')) {
                // 存在半对的答案
                const ansArr = answerHistory[qIndex]
                    .map(record => record.answer.trim())
                    .flatMap(str => str.includes(',') ? str.split(',').map(s => s.trim()) : str.split(''));
                ansArr.forEach(ch => {
                    answerTable[qIndex][ch.charCodeAt(0) - 'A'.charCodeAt(0)] = 1; 
                });
            } else {
                console.log('before修补的answerTable:', answerTable);
                const ansArr = answerHistory[qIndex]
                    .map(record => record.answer.trim())
                    .flatMap(str => str.includes(',') ? str.split(',').map(s => s.trim()) : str.split(''));
                console.log('ansArr:', ansArr);
                const filteredArr = ansArr.filter(ch => answerTable[qIndex][ch.charCodeAt(0) - 'A'.charCodeAt(0)] !== 1);
                console.log('filteredArr:', filteredArr);
                if (filteredArr.length === 1) {
                    answerTable[qIndex][filteredArr[0].charCodeAt(0) - 'A'.charCodeAt(0)] = 0;
                }
                console.log('answerTable:', answerTable);
                //confirm('debug: 可能存在多选题答案修补问题，请检查控制台输出');
            }
            let tryAnother = true;
            let ansStr = "";
            for (let i = 0; i < options.length; i++) {
                if (answerTable[qIndex][i] === -1) {
                    if (tryAnother) {
                        ansStr += options[i].getAttribute('data');
                        tryAnother = false; 
                    } 
                } else if (answerTable[qIndex][i] === 1) {
                    ansStr += options[i].getAttribute('data');
                }
            }
            if (ansStr.length > 0) {
                answerJson.push({
                    "题号": qNum,
                    "答案": ansStr
                });
            } else {
                confirm(`题号${qNum}未找到任何有效答案`);
            }

        } else if (type === 'judge') { // 判断题
            const options = quesDiv.querySelectorAll('span.num_option_dx');
            if (answerTable[qIndex].length === 0) {
                answerTable[qIndex] = Array(options.length).fill(-1);
            }

            if (answerHistory[qIndex]?.some(record => record.mark === 'right')) {
                answerJson.push({
                    "题号": qNum,
                    "答案": answerHistory[qIndex][0]?.answer || ""
                });
                return;
            } else {
                let ansStr = answerHistory[qIndex][0]?.answer;
                ansStr = (ansStr[0] === '对' || ansStr[0] === 'A' || ansStr === 'true') ? 'false' : 'true';
                if (ansStr) {
                    answerJson.push({
                        "题号": qNum,
                        "答案": ansStr
                    });
                } else {
                    confirm(`题号${qNum}未找到任何有效答案`);
                }
            }
        } else { // 单选题
            const options = quesDiv.querySelectorAll('span.num_option_dx');
            if (answerTable[qIndex].length === 0) {
                answerTable[qIndex] = Array(options.length).fill(-1);
            }

            if (answerHistory[qIndex]?.some(record => record.mark === 'right')) {
                answerJson.push({
                    "题号": qNum,
                    "答案": answerHistory[qIndex][0]?.answer || ""
                });
                return;
            } else {
                let ansStr = answerHistory[qIndex][0]?.answer;
                const copy = ansStr;
                answerTable[qIndex][ansStr[0].charCodeAt(0) - 'A'.charCodeAt(0)] = 0;
                while(answerTable[qIndex][ansStr[0].charCodeAt(0) - 'A'.charCodeAt(0)] === 0) {
                    ansStr = String.fromCharCode((ansStr[0].charCodeAt(0) - 'A'.charCodeAt(0) + 1) % 4 + 'A'.charCodeAt(0));
                }
                if (ansStr && ansStr !== '\u0000') {
                    answerJson.push({
                        "题号": qNum,
                        "答案": ansStr
                    });
                } else {
                    console.log('copy:', copy);
                    console.log('ansStr:', ansStr);
                    confirm(`题号${qNum}未找到任何有效答案`);
                }
            }
        }
    });
    console.log('修补答案完成:', answerJson);
    return answerJson;
}


function getFontBase64() {
    for (const sheet of document.styleSheets) {
        try {
            for (const rule of sheet.cssRules) {
                if (rule instanceof CSSFontFaceRule
                    && rule.style.fontFamily === '"font-cxsecret"') {
                    const m = rule.style.src.match(/base64,([^)]+)/);
                    if (m) return m[1];
                }
            }
        } catch(e) {}
    }
    return '';
}

function _nodeToText(element, images) {
    if (!element) return '';
    const parts = [];
    for (const child of element.childNodes) {
        if (child.nodeType === 3) {
            parts.push(child.textContent);
        } else if (child.nodeName === 'IMG' && child.src) {
            const idx = images.length;
            images.push({ index: idx, src: child.src });
            parts.push('[' + '图片#' + idx + ']');
        } else {
            parts.push(_nodeToText(child, images));
        }
    }
    return parts.join('');
}

function extractQuizData(doc) {
    const questions = [];
    const images = [];
    for (const q of doc.querySelectorAll('.TiMu.newTiMu')) {
        const num = q.querySelector('i.fl')?.textContent.trim() ?? '';
        const qtype = q.querySelector('.newZy_TItle')?.textContent.trim() ?? '';
        const stem = _nodeToText(q.querySelector('.fontLabel'), images);
        const options = [...q.querySelectorAll('li')].map(li => _nodeToText(li, images));
        questions.push({ num, type: qtype, stem, options });
    }
    return { questions, images };
}
