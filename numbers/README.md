# Filecoin In Numbers 📈

A dashboard to surface the most important Filecoin Metrics coming from the [Filecoin Data Portal datasets](https://filecoindataportal.xyz).

This is an [Observable Framework](https://observablehq.com/framework) project!

## 📊 Data Sources

This dashboard uses data from several sources in the [Filecoin Data Portal](https://filecoindataportal.xyz):

Data is refreshed daily and metrics are calculated using SQL queries against these datasets. The visualizations leverage [Observable Plot](https://observablehq.com/plot/) for interactive charts.

## 🎨 Features

- Clean, minimal dashboard interface
- Interactive time series charts
- Filter metrics by timeframe
- Key metrics across data onboarding, users, power, retrievals, sectors, economics, transactions, gas usage and developer activity
- 30-day moving averages to reduce noise
- Responsive design that adapts to different screen sizes

## 🛠️ Architecture

The dashboard is built using:

- Observable Framework for app structure and reactivity
- D3.js and Observable Plot for visualization
- DuckDB for data processing
- GitHub Actions for automated builds and deploys
- Cloudflare Pages for hosting

## 🔧 Development

Starting to work on it only takes a few seconds. To start the local preview server, run:

```bash
npm run dev
```

Then visit <http://localhost:3000> to preview your project.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
