document.addEventListener("DOMContentLoaded", function () {
    const unitButtons = document.querySelectorAll('.temp-unit');
    let currentUnit = 'c';

    // === Переключение температуры ===
    unitButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            unitButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const unit = this.getAttribute('data-unit');
            if (unit !== currentUnit) {
                convertTemps(unit);
                currentUnit = unit;
            }
        });
    });

    function convertTemps(toUnit) {
        const temps = document.querySelectorAll('.temperature, .temp');
        temps.forEach(el => {
            const celsius = parseFloat(el.getAttribute('data-celsius'));
            if (isNaN(celsius)) return;

            el.innerText = toUnit === 'f'
                ? `${(celsius * 9 / 5 + 32).toFixed(1)}°F`
                : `${celsius.toFixed(1)}°C`;
        });
    }

    // === Обновление погодных данных ===
    const weatherApiUrl = "/api/current/";
    const chartUrl = "/chart-data/";

    function updateWeatherData() {
        fetch(weatherApiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.temperature !== undefined) {
                    const tempEl = document.querySelector('.temperature');
                    tempEl.textContent = `${data.temperature.toFixed(1)}°C`;
                    tempEl.setAttribute('data-celsius', data.temperature.toFixed(1));

                    document.querySelector('.humidity').textContent = `${data.humidity}%`;
                    document.querySelector('.pressure').textContent = `${data.pressure} Pa`;
                    document.querySelector('.wind').textContent = `${data.wind} м/с`;
                    document.querySelector('.visibility').textContent = `${data.cloudiness}`;
                    document.getElementById('current-time').textContent = data.timestamp;
                    document.getElementById('current-date').textContent = data.date;

                    if (currentUnit === 'f') convertTemps('f');
                }
            })
            .catch(err => console.error("Ошибка обновления погоды:", err));
    }

    function updateChart() {
        fetch(chartUrl)
            .then(response => response.json())
            .then(data => {
                if (data.chart) {
                    document.getElementById('tempChart').src = data.chart;
                }
            })
            .catch(err => console.error("Ошибка обновления графика:", err));
    }

    // === Синхронизированный запуск в начале каждой минуты ===
    function getDelayToNextMinute() {
        const now = new Date();
        return (60 - now.getSeconds()) * 1000 - now.getMilliseconds();
    }

    function scheduleMinutely(func) {
        func(); // сразу выполнить
        const delay = getDelayToNextMinute();
        setTimeout(() => {
            func();
            setInterval(func, 60000);
        }, delay);
    }

    scheduleMinutely(updateWeatherData);
    scheduleMinutely(updateChart);
    function startClock() {
    function updateClock() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const dateStr = now.toLocaleDateString('ru-RU');
        const timeEl = document.getElementById('current-time');
        const dateEl = document.getElementById('current-date');
        if (timeEl) timeEl.textContent = timeStr;
        if (dateEl) dateEl.textContent = dateStr;
    }

    updateClock(); // сразу при загрузке
    setInterval(updateClock, 1000); // каждую секунду
}
startClock();
});
