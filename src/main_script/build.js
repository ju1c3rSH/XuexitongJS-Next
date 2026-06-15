const fs = require('fs');
const path = require('path');

const ORDER = ['core', 'nav', 'video', 'pdf', 'quiz', 'main'];
const dir = path.join(__dirname, 'modules');

let output = '/* uXueXiTongX auto-built */\n';
for (const name of ORDER) {
    output += fs.readFileSync(path.join(dir, `${name}.js`), 'utf-8');
    output += '\n\n';
}
fs.writeFileSync(path.join(__dirname, 'script.js'), output);
console.log(`Built: ${output.length} chars`);
