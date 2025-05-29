document.addEventListener("DOMContentLoaded", function () {
    const unitButtons = document.querySelectorAll('.temp-unit');
    let currentUnit = 'c';

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
            if (toUnit === 'f') {
                el.innerText = `${(celsius * 9 / 5 + 32).toFixed(1)}°F`;
            } else {
                el.innerText = `${celsius.toFixed(1)}°C`;
            }
        });
    }

    // Текущее время и дата
    const timeEl = document.getElementById("current-time");
    const dateEl = document.getElementById("current-date");

    const days = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
    const months = ["января", "февраля", "марта", "апреля", "мая", "июня", 
                    "июля", "августа", "сентября", "октября", "ноября", "декабря"];

    function updateDateTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, "0");
        const minutes = now.getMinutes().toString().padStart(2, "0");
        const seconds = now.getSeconds().toString().padStart(2, "0");
        timeEl.textContent = `${hours}:${minutes}:${seconds}`;
        const day = now.getDate();
        const month = months[now.getMonth()];
        const weekday = days[now.getDay()];
        dateEl.textContent = `${day} ${month}, ${weekday}`;
    }

    updateDateTime(); 
    setInterval(updateDateTime, 1000); 
});
