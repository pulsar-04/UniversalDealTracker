# 🚀 Universal Deal Tracker

> An advanced, automated web scraping and tracking platform designed to monitor local car markets and IT job boards. 

Universal Deal Tracker is not just a scraper; it's a fully automated system that utilizes background processing to continuously monitor external platforms, track price fluctuations over time, and alert users of new opportunities. Built with a focus on scalable architecture and clean UI.

## ✨ Key Features

* **🤖 Modular Multi-Scraping Architecture:** Extensible Object-Oriented scrapers designed to parse completely different DOM structures (Mobile.bg, Cars.bg, Dev.bg) through a unified interface.
* **🕰️ Background Task Automation:** Utilizes Celery (and Django management commands) to execute long-running scraping tasks asynchronously without blocking the main application thread.
* **📈 Historical Price Analytics:** Implements relational database design (`ForeignKey`) to track and store price changes over time. Visualizes this data dynamically on the frontend using `Chart.js`.
* **🛡️ Smart Anti-Scraping Bypass:** Custom logic to handle WordPress Canonical Redirects, AJAX-based pagination (FacetWP), and infinite loop protections.
* **📧 Automated Email Alerts:** Real-time notifications sent to users when new items matching their specific criteria are found.
* **✨ Modern "Glassmorphism" UI:** A sleek, responsive, dark-mode frontend built with modern CSS techniques and Bootstrap components.

## 🛠️ Tech Stack

**Backend & Architecture:**
* Python 3.x
* Django (MVT Architecture)
* PostgreSQL (Relational Database)
* Celery & Redis (Background Task Queue)
* Docker & Docker Compose (Containerization)

**Data Extraction:**
* BeautifulSoup4
* Requests (with custom User-Agent management)
* Regular Expressions (RegEx) for robust DOM element targeting

**Frontend:**
* HTML5 / CSS3 / JavaScript
* Bootstrap 5
* Chart.js (Data Visualization)

## 🧠 Technical Highlights & Challenges Overcome

During the development of this project, several complex engineering challenges were resolved:

1. **Bypassing Dynamic Pagination (AJAX):** External sites like Dev.bg use JavaScript-heavy plugins (FacetWP) that hide standard pagination URLs. I engineered a URL-construction approach bypassing the DOM entirely, allowing the Python scraper to force-iterate through hidden pages.
2. **Canonical Redirect Loops:** Implemented "defensive programming" checks to detect when external servers attempt to secretly redirect the scraper back to page 1, preventing infinite loops and database duplication.
3. **Price History Tracking:** Transitioned from a simple `update_or_create` logic to a sophisticated state-checking mechanism. The system now compares incoming live data against historical database records to log specific price drops and generate accurate trend charts.

## 🚀 Local Setup & Installation

The application is fully containerized for a seamless setup experience.

1. Clone the repository:
   git clone https://github.com/pulsar-04/UniversalDealTracker.git
   cd UniversalDealTracker

2. Start the Docker containers:
   docker compose up -d --build

3. Run database migrations:
   docker compose exec web python manage.py migrate

4. Create a superuser for the Admin Panel:
   docker compose exec web python manage.py createsuperuser

5. Access the application:
   * Main App: http://127.0.0.1:8000
   * Admin Panel: http://127.0.0.1:8000/admin

## 👨‍💻 About the Developer
Built as a portfolio project to demonstrate backend engineering, database management, and asynchronous task handling capabilities. Open to Backend / Full-Stack internship and junior opportunities.
