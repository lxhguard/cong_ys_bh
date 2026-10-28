# this 指向

## 0. 核心结论（笔记原话，背这四句）

- **this 指向最后调用当前代码的那个对象** —— `谁调用 this，this 指向谁`
- **箭头函数的 this 在定义时确定**，指向外层代码块的 this（即被创建时的环境）
- `var` 默认绑定到 window；`let`、`const` 不会
- 判断口诀：先看调用形式 → 再定 this；箭头函数永远先排除

## 1. this 指向的四种情况

| 调用方式 | this 指向 | 典型示例 |
| --- | --- | --- |
| 直接调用 `fn()` | `window` | `fn()` |
| 函数里调用（裸调用） | `window` | 回调、定时器、赋值后调用 |
| `new` 调用 | 创建的新实例对象 | `new Person()` |
| 对象方法调用 `obj.fn()` | 调用它的对象 `obj` | `obj.getA()` |
| 箭头函数方法 | **被创建时的环境**（定义时） | `sayA: () => {}` → window |

## 2. 改变 this 指向的四种方式

`new` / `bind` / `call` / `apply`

| 方式 | 传参形式 | 执行时机 | 返回 |
| --- | --- | --- | --- |
| `call` | 参数列表 `fn.call(obj, 1, 2)` | **立即执行** | 函数结果 |
| `apply` | 参数数组 `fn.apply(obj, [1, 2])` | **立即执行** | 函数结果 |
| `bind` | 参数列表，**可多次传** `fn.bind(obj)(1, 2)` | 返回后**稍后调用** | **绑定 this 的新函数** |
| `new` | 构造函数 | 立即创建 | 新实例对象 |

> 
> 区别一句话：apply 是数组、call 是参数列表；apply/call 一次性传参立即执行，bind 可分多次传参、返回函数留到后面调用。

## 3. 面试题精讲（你的原题 + 解析）

**题 1：箭头函数在方法里，指向创建时的环境**

```
function M() {
  const a = 1;
  let obj = {
    a: 2,
    sayA: () => { console.log(this.a, this); },
  };
  obj.sayA();
}
M(); // undefined window
```

解析：`sayA` 是箭头函数，**无视 `obj` 调用**，this 在定义时捕获外层 `M` 的环境；`M()` 直接调用 this 是 window，`window.a` 不存在 → `undefined`。

**题 2：普通函数 vs 箭头函数，同一个对象两个答案**

```
a = 1;
obj = {
  a: 2,
  getA: function () { console.log(this.a, this); }, // 对象方法 → this 是 obj
  sayA: () => { console.log(this.a, this); },       // 箭头函数 → this 是 window
};
obj.getA(); // 2 obj
obj.sayA(); // 1 window
```

解析：普通函数「谁调用指向谁」→ obj；箭头函数「定义时确定」→ window（`a=1` 是全局）。

**题 3：函数里调用指向 window（注意全局变量污染）**

```
a = 300;
function A() {
  a = 100;                // 没写 var/let → 改的是全局 window.a
  console.log(this.a);    // this 是 window → 100
}
A(); // 100

function B() {
  const a = 200;          // 局部 a，不影响 window.a
  console.log(this.a);    // this 是 window → 100（上一步改的）
}
B(); // 100
```

**题 4：隐式丢失——方法拆出来就丢 this**

```
this.x = 9;
var module = { x: 81, getX: function () { return this.x; } };
var retrieveX = module.getX;   // 方法被"拆下来"了
retrieveX();       // 9   ← 裸调用 → window.x
var boundGetX = retrieveX.bind(module);
boundGetX();       // 81  ← bind 显式绑定 → module.x
```

**题 5：赋值表达式返回函数 → 裸调用**

```
function foo() { console.log(this.a); }
var a = 2;
var o = { a: 3, foo: foo };
var p = { a: 4 };
o.foo();          // 3   ← obj.method() → this 是 o
(p.foo = o.foo)(); // 2   ← 赋值表达式返回裸函数 → this 是 window → window.a=2
```

**题 6：let/const 不挂 window**

```
let a = 10;
const b = 20;
function foo() {
  console.log(this.a); // undefined ← this 是 window，window 上没有 a（let 不挂）
  console.log(this.b); // undefined
}
foo();
console.log(window.a); // undefined
```

## 4. 补充易错点（升级新增）

| 易错点 | 结论 |
| --- | --- |
| 严格模式裸调用 | this 是 `undefined`，不是 window（class 内部默认严格模式） |
| `bind` 之后再 `call` | 改不了，this 被 bind 锁定 |
| `new` 覆盖 `bind` | `new (f.bind(a))()` → this 是新对象，不是 a |
| 回调/定时器传方法 | `setTimeout(obj.method, 100)` this 丢 → 用箭头函数或 bind |
| 箭头函数 | 没有自己的 this，`call/bind` 无效，**不能 new** |
| 优先级 | `new > bind/显式 > 隐式 > 默认`；箭头函数插在所有规则之前 |

## 5. 自测 3 题（30 秒内答出）

```
// ①
const obj = { x: 1, fn: function () { return this.x; } };
const f = obj.fn;
console.log(f());        // ? → undefined（window.x）

// ②
const o = { x: 2, fn: () => this.x };
console.log(o.fn());     // ? → undefined（箭头函数，定义时是全局）

// ③
function P() { this.x = 3; }
const C = P.bind({ x: 4 });
console.log(new C().x);  // ? → 3（new 覆盖 bind）
```

---

下面这张「谁调用 this 指向谁」映射图，配合你的记忆口诀复习：

```
<html style="margin:0;padding:0;">
<title>this指向映射图（谁调用指向谁）</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">谁调用 this，this 指向谁</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">按调用形式判断；箭头函数优先排除（定义时确定）</div>
  <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:stretch;">
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #e5484d;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#b91c1c;">直接调用 / 函数里调用</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">→ <b>window</b>（严格模式 undefined）</div>
    </div>
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #16a34a;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#15803d;">new 调用</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">→ <b>新实例对象</b></div>
    </div>
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #3b82f6;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#1d4ed8;">对象方法调用 obj.fn()</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">→ <b>obj</b>（谁调用指向谁）</div>
    </div>
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #8b5cf6;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#6d28d9;">箭头函数方法</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">→ <b>定义时的外层环境</b>（如 window）</div>
    </div>
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #f76b15;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#c2410c;">call / apply / bind</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">→ <b>传入的对象</b>；bind 锁定、new 可覆盖</div>
    </div>
  </div>
  <div style="margin-top:14px;background:#fffbeb;border-left:4px solid #d97706;border-radius:8px;padding:10px 14px;font-size:13px;color:#92400e;">
    记忆链：<b>裸调用→window｜new→新对象｜obj.fn()→obj｜箭头→定义时</b>；改变指向：<b>new / bind / call / apply</b>（apply 数组、call 列表、bind 返回函数多次传参）。
  </div>
</div>
```
