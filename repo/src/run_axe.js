const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

const pagesDir = path.join(__dirname, '..', 'pilot', 'pages');
const resultsDir = path.join(__dirname, '..', 'pilot', 'results');
if (!fs.existsSync(resultsDir)) fs.mkdirSync(resultsDir);

const files = fs.readdirSync(pagesDir).filter(f => f.endsWith('.html'));

async function runOne(file) {
  const html = fs.readFileSync(path.join(pagesDir, file), 'utf8');
  const dom = new JSDOM(html, { runScripts: 'outside-only', resources: undefined, url: 'http://localhost/' });
  const { window } = dom;

  // inject axe-core into the jsdom window
  window.eval(axeSource);

  return new Promise((resolve, reject) => {
    window.axe.run(window.document, {
      // run only checks relevant to rules ClearSite implements, plus a couple standard ones,
      // to keep the comparison meaningful rather than axe's full ruleset
      runOnly: {
        type: 'rule',
        values: [
          'image-alt', 'color-contrast', 'label', 'link-name', 'heading-order'
        ]
      }
    }, (err, results) => {
      if (err) return reject(err);
      resolve(results);
    });
  });
}

(async () => {
  const summary = {};
  for (const file of files) {
    const name = path.basename(file, '.html');
    try {
      const results = await runOne(file);
      const violations = results.violations.map(v => ({
        rule: v.id,
        impact: v.impact,
        help: v.help,
        nodes: v.nodes.map(n => ({
          target: n.target,
          html: n.html,
          failureSummary: n.failureSummary
        }))
      }));
      summary[name] = violations;
      fs.writeFileSync(
        path.join(resultsDir, `axecore_${name}.json`),
        JSON.stringify(violations, null, 2)
      );
      console.log(`=== ${name} ===`);
      console.log(`axe-core violations: ${violations.reduce((n, v) => n + v.nodes.length, 0)} (across ${violations.length} rule types)`);
      for (const v of violations) {
        console.log(`  [${v.impact}] ${v.rule} (${v.nodes.length}x) - ${v.help}`);
      }
      console.log('');
    } catch (e) {
      console.error(`Error on ${name}:`, e.message);
    }
  }
  fs.writeFileSync(path.join(resultsDir, 'axecore_summary.json'), JSON.stringify(summary, null, 2));
})();
