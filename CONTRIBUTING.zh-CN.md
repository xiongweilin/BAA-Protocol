# 贡献指南

> [English](CONTRIBUTING.md) | 简体中文

BAA-Protocol 是一个研究原型，关注有条件保证与 bounded action admission。贡献应保持“模型属性、实验性证据、真实部署声明”三者之间的区别。

## 提交变更前

- 明确说明该变更影响的 behavior、assumption 或 claim。
- 所有 guarantee 都必须限定在声明的 domain、interface、horizon 与 evidence 内。
- 改变 protocol behavior 时，应提供可复现 test 或 experiment evidence。
- 不得把与固定 AIOS surface 的 compatibility 描述成 production certification。

## 运行参考测试

在仓库根目录执行：

~~~powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/run_offboarding_experiment.py
python scripts/run_delegation_frontier.py
python scripts/run_delegation_study.py
~~~

AIOS compatibility suite 在 <code>.github/workflows/tests.yml</code> 中针对固定 AIOS revision 运行。涉及该 integration 的变更应保持现有 pin，或显式更新 pin 及其 compatibility evidence。

对于实质性的 protocol 或 experiment-design 改动，建议在大规模实现前先开 issue。Pull request 应总结变化的 claim/behavior，以及用于评价它的 evidence。
