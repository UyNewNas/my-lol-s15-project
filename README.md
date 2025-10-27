# LOLS15 英雄联盟S15赛季数据可视化项目

这是一个用于展示英雄联盟S15赛季比赛数据的前端可视化项目，支持入围赛、瑞士轮和淘汰赛数据的查看与分析。

## 项目功能

- **比赛数据可视化**：展示不同阶段（入围赛、瑞士轮、淘汰赛）的比赛数据
- **战队战绩查询**：查看各战队在不同阶段的战绩表现
- **赛程展示**：按时间顺序和比赛轮次展示赛程安排
- **实时数据更新**：通过JSON文件存储和更新比赛数据

## 项目结构

```
LOLS15/
├── index.html      # 主页面文件
├── lol_s15_schedule.json  # 比赛数据JSON文件
├── lol_s15_scrape.py      # 数据爬取脚本（如果有）
├── requirements.txt       # Python依赖文件
└── README.md              # 项目说明文档
```

## 技术栈

- **前端**：HTML, CSS, JavaScript
- **数据存储**：JSON
- **服务器**：Python HTTP Server
- **数据获取**：可能使用Python爬虫（见lol_s15_scrape.py）

## 如何使用

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd LOLS15
```

### 2. 启动本地服务器

使用Python的内置HTTP服务器启动项目：

```bash
python -m http.server 8000
```

然后在浏览器中访问：`http://localhost:8000`

### 3. 数据更新

如需更新比赛数据，修改 `lol_s15_schedule.json` 文件即可。文件格式如下：

```json
{
  "YYYY-MM-DD": {
    "date": "YYYY-MM-DD",
    "total_matches": 8,
    "matches": {
      "match_id": {
        "match_id": 32592,
        "match_name": "瑞士轮",
        "match_start_time": "YYYY-MM-DD HH:MM:SS",
        "match_end_time": "YYYY-MM-DD HH:MM:SS",
        "match_status": "已结束",
        "match_away_team": "队伍A",
        "match_away_score": 0,
        "match_home_team": "队伍B",
        "match_home_score": 1,
        "date": "YYYY-MM-DD"
      }
      // 更多比赛...
    }
  }
  // 更多日期...
}
```

## 页面导航

- **入围赛**：查看入围赛阶段的所有比赛
- **瑞士轮**：按轮次查看瑞士轮比赛和战队排名
- **淘汰赛**：查看四分之一决赛、半决赛和决赛
- **战队**：按赛区查看所有参赛战队

## 开发说明

### 数据加载流程

1. 页面加载时，JavaScript通过`fetch` API从`lol_s15_schedule.json`读取数据
2. 数据加载后，通过`categorizeMatches`函数按比赛阶段分类
3. 分类后的数据存储在全局变量中供渲染函数使用

### 添加新功能

1. 在`index.html`中找到相应的功能模块
2. 修改或添加相关JavaScript代码
3. 确保数据格式与现有逻辑兼容

## 注意事项

- 比赛数据时间格式为`YYYY-MM-DD HH:MM:SS`
- 瑞士轮轮次计算基于日期（10月15日为第1轮，10月16日为第2轮，以此类推）
- 页面使用简单的HTTP服务器，生产环境部署时建议使用专业的静态文件服务器

## License

MIT License

## Acknowledgments

- 感谢所有为这个项目做出贡献的开发者
- 数据来源：英雄联盟官方赛事数据