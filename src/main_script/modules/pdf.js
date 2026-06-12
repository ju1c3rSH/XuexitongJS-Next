function findPdfElement(innerDoc) {
    const finalIframe = innerDoc.getElementById(PDF_IFRAME_ID);
    if (!finalIframe) {
        console.log('[调试] 未找到 panView 元素');
        return null;
    }
    let finalDoc;
    try {
        finalDoc = finalIframe.contentDocument || finalIframe.contentWindow.document;
    } catch (e) {
        console.log('[调试] 获取 panView 的 document 失败', e);
        return null;
    }
    
    const pdfHtml = finalDoc.documentElement;
    if (!pdfHtml) {
        console.log('[调试] 未找到 pdf 元素');
        return null;
    }

    const pdfBody = finalDoc.body;
    if (!pdfBody || !pdfBody.childNodes || pdfBody.childNodes.length === 0) {
        console.log('[调试] PDF 文档 body 为空或不存在');
        return null;
    }
    console.log('已找到 pdf 元素:', pdfHtml);
    return { pdfHtml };
}

function scrollPdfToBottom(pdfHtml, maxTries = Math.floor(DEFAULT_TRY_COUNT / 10)) { 
    return new Promise(async (resolve) => {
        let lastTop = pdfHtml.scrollTop;
        let tries = 0;
        while (tries < maxTries) {
            pdfHtml.scrollTo({
                top: pdfHtml.scrollHeight,
                behavior: 'smooth'
            });
            await timeSleep(4 * DEFAULT_SLEEP_TIME); // 等待滚动动画
            if (pdfHtml.scrollTop !== lastTop && pdfHtml.scrollTop > 0) {
                resolve(true); // 滚动成功
                return;
            }
            lastTop = pdfHtml.scrollTop;
            tries++;
        }
        resolve(false); // 多次尝试后仍未滚动
    });
}
