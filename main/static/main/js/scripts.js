document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".temp-switch .temp-unit");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            if (this.classList.contains("active")) return;

            buttons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            const selectedUnit = this.getAttribute("data-unit");
            console.log("Выбрана единица:", selectedUnit);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const timeEl = document.getElementById("current-time");
    const dateEl = document.getElementById("current-date");

    const days = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
    const months = ["января", "февраля", "марта", "апреля", "мая", "июня", 
                    "июля", "августа", "сентября", "октября", "ноября", "декабря"];

    function updateDateTime() {
        const now = new Date();

        // Текущее время (с секундами)
        const hours = now.getHours().toString().padStart(2, "0");
        const minutes = now.getMinutes().toString().padStart(2, "0");
        timeEl.textContent = `${hours}:${minutes}`;

        // Текущая дата
        const day = now.getDate();
        const month = months[now.getMonth()];
        const weekday = days[now.getDay()];
        dateEl.textContent = `${day} ${month}, ${weekday}`;
    }

    updateDateTime(); // первая загрузка
    setInterval(updateDateTime, 1000); // обновление каждую секунду
});


