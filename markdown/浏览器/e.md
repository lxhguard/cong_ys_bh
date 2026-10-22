# 从输入 URL 到页面加载

面试话术对照稿。同一道题两套答法：

- **P6**：按八阶段讲清「原理 + 优化点」
- **P7**：立流水线模型，讲「瓶颈判断 + 优化杠杆 + 指标归因 + 因果实战」

---

# 一、P6 回答

P6 版是**可直接背诵的完整话术稿**，按「开场 → 八阶段 → 收尾」组织。重点段（TCP/TLS、缓存、渲染）已加粗，方便识别要展开的地方。

## 开场（约 20 秒）

> 整个过程我可以分成八步：**URL 解析、DNS 解析、TCP 连接（HTTPS 还有 TLS 握手）、发送 HTTP 请求、服务器响应、浏览器解析渲染、加载完成事件、连接复用与关闭**。我按这个顺序讲，每步会带上原理和常见的优化点。

## ① URL 输入与解析（约 15 秒）

> 浏览器先处理地址栏输入：补全协议、通过 HSTS 强制走 HTTPS，然后解析出协议、域名、端口、路径、参数和锚点。如果输入的不是合法网址，会被当成搜索词交给搜索引擎；有非法字符会先转义。

### ① 追问展开 · 补全协议 / HSTS / 非法字符

话术里三个词，面试官常逐个追问。顺序记成：**补全协议 → HSTS → 转义 → 拆分组件**。

#### 补全协议

地址栏往往只敲 `jd.com` 或 `www.jd.com`，没有 `http://` / `https://`。浏览器会先**补全协议**再解析：

- 有 HSTS 记录 / 默认偏好 HTTPS 时 → 补成 `https://`
- 否则历史上常补 `http://`，再由 301/HSTS 升到 HTTPS
- 已是完整 URL（带协议）则跳过这一步

一句话：**补全协议是「把人类输入变成可解析的绝对 URL」**，后面的 HSTS、转义、拆组件都建立在这个绝对 URL 上。

#### HSTS（HTTP Strict Transport Security）

HSTS（HTTP 严格传输安全）是**浏览器侧强制 HTTPS** 的机制，专门防「降级攻击 / SSL stripping」。

**一句话原理**：服务器在响应头声明一段时间只许走 HTTPS，浏览器记住后，即便用户输入 `http://` 或点了 http 链接，也会**先升级成 HTTPS 再发请求**，且不允许跳过证书警告。

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

- `max-age`：记忆多久（秒）
- `includeSubDomains`：子域一并生效（可选还有 `preload` 进浏览器内置名单）

**它解决什么问题**：中间人做 SSL stripping 时，把 https 悄悄换成 http，全程明文，浏览器仍可能显示「已连接」，用户无感。HSTS 等于告诉浏览器——「这个域名只能 HTTPS，见到 http 一律升级，别信」，中间人没法降级。

#### 非法字符与百分号编码

「非法字符」指的是**不在 URL 合法字符集里、或者会破坏 URL 结构的字符**。浏览器处理方式是**百分号编码（percent-encoding）**：先把字符转成 UTF-8 字节，每个字节写成 `%XX`。

**三类字符（RFC 3986 口径）**

| 类别 | 字符 | 说明 |
| --- | --- | --- |
| 合法・非保留（直接用） | A-Z a-z 0-9 - _ . ~ | 无需转义 |
| 保留字符（有特殊含义，作为普通数据时必须转义） | : / ? # [ ] @ ! $ & ' ( ) * + , ; = | 在 URL 特定位置有语法作用。例：query 参数值里出现 & 会把参数截断，必须编码成 %26 |
| 非法 / 不安全字符（必须转义） | 空格、中文等非 ASCII、" < > \ ^ ` { \| }、控制字符 | 空格 → %20（表单场景可能是 +）；中文按 UTF-8 转 |

**例子**

```
百度.com/search?q=北京 天气
```

浏览器自动转成（地址栏可显示原文，实际请求的是编码后）：

```
https://xn--wxtr44c.com/search?q=%E5%8C%97%E4%BA%AC%20%E5%A4%A9%E6%B0%94
```

- 域名里的中文 → **Punycode**（`xn--wxtr44c`），不是百分号编码
- 路径/查询里的中文和空格 → UTF-8 + `%XX`

**面试会追问的两个点（背熟）**

1. **`encodeURIComponent` vs `encodeURI` 的区别**（JS 高频题）
   - `encodeURI`：只编码非法字符，**保留** `:/?#` 等语法字符 → 用于编码整个 URL
   - `encodeURIComponent`：连保留字符一起编码 → 用于编码**单个参数值**（否则 `&`、`=` 会破坏结构）
2. **浏览器会自动转义吗？** 会——地址栏输入中文/空格，浏览器在发请求前自动完成编码；所以「非法字符转义」这一环讲的是**浏览器内部行为**，用户基本无感知。

一句话接回链路：**「补全协议 → HSTS → 转义 → 拆分组件」里的转义，本质就是把非法/有歧义字符换成 `%XX`，保证 URL 语法不被破坏。**

## ② DNS 解析（约 30 秒）

> 域名要翻译成 IP。查询顺序是**浏览器缓存 → 操作系统缓存和 hosts → 本地 DNS 服务器（LDNS）**。LDNS 自己也不知道的话，就向根域名服务器问，根服务器告诉它去问谁，逐级迭代到顶级域名服务器、权威域名服务器，拿到 A 记录或 CNAME 别名后返回并逐级缓存。
>
> 优化点是：多级缓存就是最快路径；前端可以加 `dns-prefetch` 提前解析；大站还会通过 CDN 做 DNS 负载均衡，返回离用户最近的节点。

## ③ TCP 三次握手 + TLS（约 60 秒，重点段）

> 拿到 IP 后，因为 HTTP 基于 TCP，要先三次握手建立可靠连接：
> **第一次客户端发 SYN（seq=x）；第二次服务端回 SYN+ACK（seq=y, ack=x+1）；第三次客户端发 ACK（ack=y+1）**。三次握手的原因是理论最小值——它双向确认了双方的序列号，而且能防止失效的连接请求到达服务端后被误认为新连接、白占资源。
>
> 如果是 HTTPS，握手之后再走 TLS：**客户端发 ClientHello，服务端回 ServerHello、数字证书和公钥，客户端校验证书链、用公钥加密预主密钥发回去，双方各自派生会话密钥**。之后数据用对称加密传输，安全性来自证书链校验 + 非对称交换对称密钥。TLS 1.2 要两个 RTT，**TLS 1.3 已经压到一个 RTT**。

## ④ 发送 HTTP 请求（约 30 秒）

> 浏览器构建请求报文：**请求行（方法 + URL + 版本）、请求头（Host、User-Agent、Accept、Cookie、Cache-Control 等）、空行和请求体**。GET 和 POST 的区别本质是语义：GET 幂等、可缓存、参数在 URL；POST 不幂等、参数在 body。连接上优先复用 keep-alive 的 TCP 连接，减少建连开销。

## ⑤ 服务器响应与缓存（约 60 秒，重点段）

> 服务器返回响应报文：**状态行、响应头、空行、响应体**。状态码按类记：**2xx 成功、3xx 重定向、4xx 客户端错误、5xx 服务端错误**；常见的有 200、301/302（永久/临时重定向）、304、400、401/403、404、500/504。
>
> 这里我要重点讲缓存，因为它直接影响请求是否发出。**强缓存**：响应头带 `Cache-Control: max-age` 或 `Expires`，在有效期内浏览器直接用本地缓存，**不发请求**；**协商缓存**：强缓存过期后，请求带上 `If-None-Match`（ETag）或 `If-Modified-Since`（Last-Modified），服务器判断资源没变就返回 304，浏览器继续用缓存。**ETag 比 Last-Modified 更准**，因为它是内容指纹，Last-Modified 精度只有秒级。生产上常见策略是：带 hash 的文件名 + 长 max-age，配合 CDN。

## ⑥ 浏览器解析渲染（约 90 秒，重点段）

> 渲染过程是：**HTML 解析成 DOM 树，CSS 解析成 CSSOM，两者合成渲染树，再布局（Layout）、绘制（Paint）、合成（Composite）**。
>
> 两个关键点：第一，**JS 会阻塞 DOM 解析**——因为脚本可能修改 DOM，所以遇到同步 script 会暂停解析，等下载执行完再继续；优化手段是 `async`/`defer`，defer 保序且在解析完后执行。但浏览器有 **preload scanner**，解析被阻塞时仍会并行预下载后面的资源。第二，**CSS 不阻塞 DOM 解析，但阻塞渲染，也阻塞 JS 执行**——脚本执行前必须等 CSSOM 就绪。
>
> 布局和绘制对应两个性能概念：**回流（reflow）是位置尺寸变化，需要重新计算布局；重绘（repaint）是颜色等不影响布局的属性**。回流比重绘更贵，常见的优化是批量修改样式、把动画元素移出文档流；**transform 和 opacity 的变化走合成层，不触发回流重绘**。另外渲染完成前还有事件循环：宏任务、微任务，Promise 的微任务先于 setTimeout 执行。

## ⑦ 加载完成事件（约 15 秒）

> **DOMContentLoaded 在 DOM 树构建完就触发；load 要等图片等所有资源加载完**。现代性能指标还会看 FCP、LCP——FCP 是首次内容绘制，LCP 是最大内容元素出现的时间。

## ⑧ 连接复用与关闭（约 15 秒）

> 连接上 HTTP/1.1 靠 keep-alive 复用，HTTP/2 用多路复用，一个连接并发多个请求，还能头部压缩；HTTP/3 换 QUIC，彻底解决 TCP 层队头阻塞。请求结束就是 TCP 四次挥手：客户端发 FIN，服务端 ACK，服务端数据发完再发 FIN，客户端最后 ACK 并等待 2MSL 关闭。之所以是四次，因为服务端收到 FIN 后可能还有数据要发，先 ACK、发完再 FIN，是半关闭。

## 收尾（约 30 秒）

> 总结一下：这条链路每一段都有优化空间——网络段靠缓存、CDN、预解析；传输段靠 HTTP/2/3；渲染段靠减少阻塞和回流重绘。我在实际项目中就做过这类优化：**在番茄小说把首屏 4 段串行请求挪进 Worker 并行预取，FCP 从 4 秒降到 2.1 秒**——本质就是缩短了「等请求」这一段。

## P6 答题要点图

8 阶段 + 时间分配 + 每段必说点（重点段标红）：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>从输入URL到页面加载：P6答题时间轴</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">P6 面试版 · 答题时间轴（总时长约 5 分钟）</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">按序讲完 8 步；标红的两段是 P6 面的主战场，必须展开讲原理</div>
  <div style="display:flex;flex-direction:column;gap:8px;">
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#475569;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">① URL 解析 · 20s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;">补全协议 / HSTS / 非法字符转义 / 区分搜索词</div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#3b82f6;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">② DNS 解析 · 30s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;">浏览器→OS/hosts→LDNS（递归）→根/顶级/权威（迭代）；A/CNAME；dns-prefetch；CDN 就近</div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;border:2px solid #e5484d;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#e5484d;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">③ TCP+TLS · 60s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;"><b>必讲：三次握手 SYN/SYN+ACK/ACK + 为什么三次（防失效 SYN + 双向确认）；TLS 证书链校验 + 非对称换对称；TLS1.3 压到 1-RTT</b></div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#8b5cf6;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">④ HTTP 请求 · 30s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;">请求行/头/体；GET vs POST（幂等/缓存/位置）；keep-alive 复用</div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;border:2px solid #e5484d;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#e5484d;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">⑤ 响应+缓存 · 60s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;"><b>必讲：状态码归类；强缓存（max-age 不发请求）vs 协商缓存（ETag→304）；ETag 优于 Last-Modified；hash 文件名+长缓存</b></div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;border:2px solid #e5484d;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#e5484d;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">⑥ 渲染 · 90s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;"><b>必讲：DOM/CSSOM→渲染树→Layout→Paint→Composite；JS 阻塞解析 / CSS 阻塞渲染和脚本执行；async/defer；preload scanner；回流 vs 重绘 + transform/opacity 走合成；宏微任务</b></div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">⑦ 完成事件 · 15s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;">DOMContentLoaded vs load；顺带提 FCP/LCP</div>
    </div>
    <div style="display:flex;align-items:stretch;background:#fff;border-radius:8px;overflow:hidden;">
      <div style="width:130px;min-width:130px;background:#16a34a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;">⑧ 连接 · 15s</div>
      <div style="flex:1;padding:8px 12px;font-size:13px;color:#374151;">keep-alive / HTTP2 多路复用 / HTTP3 QUIC；四次挥手（半关闭）</div>
    </div>
  </div>
  <div style="margin-top:14px;background:#e8f5ee;border-left:4px solid #16a34a;border-radius:8px;padding:10px 14px;font-size:13px;color:#14532d;">
    收尾套路：一句总结（每段都可优化）+ 一个实战例证（如 PIA 并行预取 FCP 4s→2.1s）。P6 版讲「原理 + 优化点」即可，不需要上指标归因方法论——那是 P7 版的差异。
  </div>
</div>
```

## P6 版要点

1. 八步必须完整不跳步
2. ③⑤⑥ 三段展开讲（约占 60% 时间）
3. 每段都带一句优化点（这是 P6 和 P5 的分界线）
4. 收尾一个实战例证就够，不用像 P7 那样给方法论

---

# 二、P7 回答

与 P6 的核心差别：**P6 讲「原理 + 优化点」，P7 讲「瓶颈判断 + 优化杠杆 + 指标归因 + 因果实战」**。项目不是罗列，而是串成一条方法论。

## 开场 · 立模型（约 30 秒）

> 这道题我不按流水账讲。从输入 URL 到页面可交互，本质是一条**流水线**，我习惯分成两段：**「网络获取」——把字节拿回来；「浏览器渲染」——把字节变成像素**。两段各有各的瓶颈、优化杠杆和度量指标。我按这个框架讲，并且每段都会带上我实际做过的落地和量化收益。

**P7 特征**：先给模型再展开。面试官的第一印象是「有系统观的人」，而不是「背流程的人」。

## 段 A · 网络获取（约 90 秒）

### 层 1 · 寻址（约 25 秒）

> 第一段是寻址：URL 解析后走 DNS。查询链是**浏览器缓存 → 操作系统/hosts → 本地 DNS（递归）→ 根/顶级/权威（迭代）**，拿到 A 记录或 CNAME。这里我要强调的不只是流程，而是**瓶颈在哪**：DNS 解析虽然通常只要几十毫秒，但每次都要走网络。所以优化杠杆是**多级缓存 + `dns-prefetch`/`preconnect` 提前建连 + CDN 就近调度**——DNS 本身就是 CDN 的调度入口。

### 层 2 · 建连与传输（约 40 秒）

> 第二段是建连与传输。TCP 三次握手建立可靠连接，HTTPS 再叠加 TLS（1.3 已压到 1-RTT）。到了传输层，真正的瓶颈是**队头阻塞**：HTTP/1.1 一个连接一个请求，靠 keep-alive 和域名分片缓解；HTTP/2 用多路复用解决了 HTTP 层队头阻塞，但 TCP 层队头阻塞还在——一个包丢了，后面的都得等；HTTP/3 换 QUIC 才算根治。所以传输层的优化杠杆是**协议升级、连接复用、请求合并与压缩**。

### 段 A · 实战（约 25 秒，因果叙事）

> 这一段的瓶颈我真实踩过：番茄小说书圈首屏有 4 段**串行依赖**的请求（step1→step4），最慢的一段要 7 秒。我当时的判断是「请求天然可并行化，只是被写成了串行」。落地是 **PIA 方案：把首屏请求全部挪进 Worker 线程并行预取，主线程直接消费结果，再用 Snapshot 做复访缓存**。收益是 FCP 4s→2.1s。

**P7 特征**：实战不是「我做过 PIA」，而是「瓶颈 → 判断 → 动作 → 收益」四段式。

## 段 B · 浏览器渲染（约 120 秒）

### 层 3 · 解析（约 45 秒）

> 第二段是渲染。字节到了以后，HTML 解析成 DOM，CSS 解析成 CSSOM。这里的瓶颈是**阻塞**：同步 JS 会暂停 DOM 解析，CSS 会阻塞渲染和脚本执行。但现代浏览器有 **preload scanner**——解析被卡住时仍然并行预下载后面的资源，所以「JS 阻塞解析、但不阻塞预下载」。优化杠杆是 **async/defer、Critical CSS、chunk 拆分**，本质是压缩关键渲染路径上「必须同步等」的东西。

### 层 4 · 渲染与交互（约 45 秒）

> 再往下是 Render Tree → Layout → Paint → **Composite**。这里要讲清楚性能的层次：**回流（布局变化）最贵、重绘次之、合成最便宜**——transform/opacity 走合成层不触发回流。所以渲染层优化杠杆是：减少回流触发（批量改样式、避免强制同步布局）、把动画挪到合成层、用并发渲染/长任务切片保护主线程。到交互层就看事件循环和长任务了。

### 段 B · 实战（约 30 秒，三个案例一条因果线）

> 这一段的三个瓶颈我都处理过：
>
> 第一个是**首屏依赖完整 bundle 和 React 运行时**——这是串行链路里的最大瓶颈。我做**伪 SSR**：把首屏必需的最小代码剥成独立 chunk 前置执行，数据经 `globalProps` 预注入直出，React 后台接管。FCP 1.5s→160ms。
>
> 第二个是 **iOS 闪白**——追根因发现是 WebKit 下 `<script defer>` 失效、首帧被脚本下载阻塞。自研 `DynamicScriptTagPlugin` 静态注入首屏脚本解决。
>
> 第三个是**低端机首屏**——通过请求瘦身 + 把 Arco Tabs 的合成层内存从 142MB 压到 24.1MB + 合并 20 次 setState 重绘，PCT90 5.28s→3.8s。

**P7 特征**：多个项目串成「我系统性治理过这条渲染链路」，而不是「我做过几个项目」。

## 指标归因方法论（约 60 秒，杀手锏）

> 最后说我的方法论。**优化之前先量化归因**，我排查慢页面不猜，按指标定位：
>
> **TTFB 高 → 问题在网络/服务端**（DNS、握手、服务器响应）；**FCP 差 → 解析与渲染启动慢**（首屏 chunk 大、JS/CSS 阻塞）；**LCP 差 → 最大内容元素**的资源或时机问题（大图、字体、被延迟发现的资源）；**TTI/INP 差 → JS 长任务**（主线程被占）。
>
> 定位之后用**灰度验证**：小流量对比、埋点监控、能回滚。我在番茄做 RL3 迁移就是这套流程——14 页存量迁移全程灰度、0 事故 0 回滚。

**P7 特征**：给出一套可复用的排查方法论 + 工程纪律（灰度、可回滚），这是 P6 版不会有的东西。

## 收尾 · tradeoff + 留追问（约 30 秒）

> 补一个 tradeoff：所有优化都有代价——HTTPS 安全换一个 RTT、缓存命中换内容新鲜度、chunk 前置换构建复杂度。所以我更看重**先量化再动手**：用指标定位瓶颈，用灰度验证收益。这是我做每个性能专项的标准流程，如果对某个环节感兴趣，我们可以深入聊。

## P7 答题结构图

与 P6 对照：五段式 + 时间分配 + 每段必说点：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>从输入URL到页面加载：P7答题结构图</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">P7 面试版 · 五段式答题结构（总时长约 5.5 分钟）</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">与 P6 版核心差异：立模型 / 讲瓶颈判断 / 挂指标归因 / 因果实战 / tradeoff 收尾</div>
  <div style="display:flex;flex-direction:column;gap:8px;">

    <div style="background:#1f2933;color:#fff;border-radius:10px;padding:10px 16px;">
      <div style="font-size:14px;font-weight:700;">开场 · 立流水线模型 · 30s</div>
      <div style="font-size:13px;color:#e5e7eb;margin-top:4px;">「不按流水账讲——两段流水线：网络获取拿字节，浏览器渲染变像素；每段有瓶颈、杠杆、指标，我带上落地和量化收益」</div>
    </div>

    <div style="background:#fff;border-left:6px solid #3b82f6;border-radius:10px;padding:10px 16px;">
      <div style="font-size:14px;font-weight:700;color:#3b82f6;">段 A · 网络获取 · 90s</div>
      <div style="font-size:13px;color:#374151;margin-top:6px;">
        <div><b>层1 寻址 · 25s</b>：DNS 缓存链（递归/迭代）+ 瓶颈是「网络往返」→ 杠杆：缓存 / dns-prefetch / preconnect / CDN 调度</div>
        <div><b>层2 建连传输 · 40s</b>：三次握手 + TLS1.3（1-RTT）+ 瓶颈是「队头阻塞」→ 杠杆：HTTP/2 多路复用 vs HTTP/3 QUIC</div>
        <div style="background:#eff6ff;border-radius:6px;padding:6px 10px;margin-top:6px;"><b>实战（因果叙事）</b>：瓶颈=4 段串行请求（step4 达 7s）→ 判断=可并行化 → 动作=PIA Worker 预取+Snapshot → 收益=FCP 4s→2.1s</div>
      </div>
    </div>

    <div style="background:#fff;border-left:6px solid #e5484d;border-radius:10px;padding:10px 16px;">
      <div style="font-size:14px;font-weight:700;color:#e5484d;">段 B · 浏览器渲染 · 120s</div>
      <div style="font-size:13px;color:#374151;margin-top:6px;">
        <div><b>层3 解析 · 45s</b>：DOM/CSSOM + 瓶颈是「阻塞」→ 杠杆：async/defer、Critical CSS、chunk 拆分；preload scanner 并行预下载</div>
        <div><b>层4 渲染交互 · 45s</b>：Render Tree→Layout→Paint→Composite + 瓶颈是「回流」→ 杠杆：合成层、避免强制同步布局、长任务切片</div>
        <div style="background:#fef2f2;border-radius:6px;padding:6px 10px;margin-top:6px;"><b>实战（一条因果线）</b>：伪 SSR chunk 前置 FCP 1.5s→160ms ｜ iOS 闪白 → DynamicScriptTagPlugin ｜ 低端机 合成层 142→24.1MB + 20 次 setState 合并 → PCT90 5.28→3.8s</div>
      </div>
    </div>

    <div style="background:#d97706;color:#fff;border-radius:10px;padding:10px 16px;">
      <div style="font-size:14px;font-weight:700;">指标归因方法论 · 60s（杀手锏）</div>
      <div style="font-size:13px;color:#fef3c7;margin-top:4px;">TTFB高→网络/服务端 ｜ FCP差→解析渲染启动 ｜ LCP差→最大内容元素 ｜ TTI/INP差→JS长任务；先量化再动手，灰度验证可回滚（RL3 迁移 14 页 0 事故）</div>
    </div>

    <div style="background:#16a34a;color:#fff;border-radius:10px;padding:10px 16px;">
      <div style="font-size:14px;font-weight:700;">收尾 · tradeoff + 留追问 · 30s</div>
      <div style="font-size:13px;color:#dcfce7;margin-top:4px;">「所有优化都有代价——安全换 RTT、命中率换新鲜度、前置换复杂度；所以我先量化再动手，这是每个专项的标准流程」→ 主动留追问接口</div>
    </div>

  </div>
  <div style="margin-top:14px;background:#e8f5ee;border-left:4px solid #16a34a;border-radius:8px;padding:10px 14px;font-size:13px;color:#14532d;">
    P6→P7 升级清单：① 开场从「按八步讲」换成「两段流水线模型」；② 每段从「讲原理」换成「瓶颈判断 + 优化杠杆」；③ 实战从「1 个例证」换成「4 个项目的因果叙事」；④ 增加指标归因方法论；⑤ 收尾加 tradeoff。P6 版背的是内容，P7 版背的是框架和判断。
  </div>
</div>
```

## 练习建议

P7 版最怕讲成 P6 版。自测三条都满足，才是 P7 水准：

1. 开场 10 秒内有没有说出「流水线 / 两段」模型
2. 每个实战是不是「瓶颈 → 判断 → 动作 → 收益」四段式
3. 结尾有没有 tradeoff
