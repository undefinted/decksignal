const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'DeckSignal';
pptx.subject = 'Deterministic PptxGenJS control artifact';
pptx.title = 'AI办公产品增长复盘与规划';
const slides = [
  ['AI办公产品增长复盘与规划', '2025 年复盘｜2026 年规划'],
  ['核心结论', '用户规模持续增长，但收入未达年度目标；2026 年重点是提升付费转化与续费率。'],
  ['关键经营数据', '注册用户：120 万\n月活用户：48 万\n付费用户：6.4 万\n收入：1280 万元\n目标收入：1500 万元'],
  ['用户与产品', '满意度：78%\n续费率：64%\n下一阶段聚焦高频办公场景、模板质量和团队协作。'],
  ['2026 年行动计划', 'Q1：优化核心工作流\nQ2：推出团队版\nQ3：完善生态集成\nQ4：复盘并扩大行业方案'],
  ['风险与下一步', '风险：获客成本上升、同质化竞争、模型成本波动。\n下一步：验证付费转化实验并建立周度指标看板。'],
];
for (const [title, body] of slides) {
  const slide = pptx.addSlide();
  slide.background = { color: 'F6F8FC' };
  slide.addText(title, { x: 0.7, y: 0.55, w: 11.2, h: 0.6, fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: '16233F' });
  slide.addText(body, { x: 0.9, y: 1.65, w: 10.5, h: 4.5, fontFace: 'Microsoft YaHei', fontSize: 20, breakLine: false, color: '263653', margin: 0.1, valign: 'mid' });
  slide.addText('DeckSignal control · PptxGenJS', { x: 0.7, y: 7.05, w: 5, h: 0.2, fontSize: 8, color: '71809B' });
}
pptx.writeFile({ fileName: 'results/raw/pilot-control/pptxgenjs/opb-business-001/deck.pptx' });
