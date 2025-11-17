# 抢票提醒器

这是一个基于 Python 的应用程序，旨在监控指定网站的门票可用性，并在选定区域有票时发送电子邮件通知。它使用 Playwright 进行网页抓取，并使用 Pydantic 进行配置管理。

## 功能

-   **门票可用性监控：** 持续检查目标 URL 的门票可用性。
-   **区域选择：** 允许用户选择要监控的特定门票区域。
-   **电子邮件通知：** 在监控区域发现门票时发送电子邮件提醒。
-   **可配置：** 易于使用的 `config.json` 文件，用于设置电子邮件详细信息和检查间隔。
-   **浏览器自动化：** 利用 Playwright 连接到现有的浏览器实例（Edge/Chrome）或启动新的实例。

## 设置说明

### 1. 克隆仓库

如果您收到的是一个仓库，请克隆它：
```bash
git clone <repository_url>
cd ticket-reminder
```
如果您收到的是一个 `dist` 文件夹，请进入该文件夹：
```bash
cd /path/to/your/folder
```

### 2. 创建并激活 Conda 环境

建议使用 Conda 管理依赖项。

```bash
conda env create -f environment.yml
conda activate ticket-reminder
```

### 3. 安装 Playwright 浏览器

此应用程序使用 Playwright 自动化浏览器交互。您需要安装必要的浏览器驱动程序。

```bash
playwright install
```
这将安装所有必要的浏览器二进制文件（Chromium、Firefox、WebKit）。如果您只想使用 Chromium（包括 Edge/Chrome），可以运行 `playwright install chromium`。

### 4. 配置 `config.json`

如果 `config.json` 文件不存在，首次运行脚本时将自动生成。您**必须**使用您的电子邮件服务器详细信息编辑此文件。

```json
{
  "send_email_notifications": true,
  "check_interval_seconds": 30,
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "smtp_user": "your_email@example.com",
  "smtp_password": "your_app_password",
}
```

-   `send_email_notifications`: 设置为 `true` 启用电子邮件通知，`false` 禁用。
-   `check_interval_seconds`: 每次检查门票可用性之间的延迟（秒）。
-   `smtp_server`: 您的 SMTP 服务器地址（例如，Gmail 为 `smtp.gmail.com`）。
-   `smtp_port`: 您的 SMTP 服务器端口（
-   `smtp_user`: 用于发送通知的电子邮件地址。
-   `smtp_password`: 您的 SMTP 用户密码。**对于 Gmail 和类似服务，您可能需要生成一个“应用密码”而不是使用您的常规帐户密码。** 请查阅您的电子邮件提供商的文档。

## 如何运行

1.  **确保浏览器正在运行（可选但推荐）：** 为了获得最佳性能并避免频繁启动浏览器，请在运行脚本之前手动打开 Microsoft Edge 或 Google Chrome。脚本将首先尝试连接到现有实例。
2.  **运行主脚本：**

    ```bash
    python main.py
    ```

3.  **按照提示操作：** 脚本将提示您输入要监控的抢票网址，然后选择您希望监控的区域。

    -   **目标 URL：** 输入您要监控的门票页面的完整 URL。脚本将自动调整包含 `/ticket/area/` 的 URL 为 `/ticket/get-area-map/` 以进行数据提取。
    -   **区域选择：** 获取可用区域后，将显示一个列表。输入您要监控的区域对应的数字，用逗号分隔（例如，`1,3,5`）。不输入任何内容直接按 Enter 键将监控所有区域。

脚本将根据配置持续检查门票可用性并发送通知。

## 项目结构

```
.
├── config.json             # 电子邮件和检查间隔的配置文件
├── environment.yml         # Conda 环境定义
├── main.py                 # 主应用程序逻辑
├── models.py               # Pydantic 配置模型
├── README.md               # 本文件
└── services/
    ├── notifier.py         # 电子邮件通知服务
    └── scraper.py          # 使用 Playwright 的网页抓取逻辑
```