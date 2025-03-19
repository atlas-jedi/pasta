/**
 * Utilitários para manipulação de fusos horários
 */
document.addEventListener("DOMContentLoaded", function () {
  const TimeCalcTimezone = {
    init: function () {
      this.setupTimezoneSearch();
    },

    setupTimezoneSearch: function () {
      // Timezone search functionality
      const timezoneSearchInput = document.getElementById("timezone-search");
      const clearTimezoneSearchBtn = document.getElementById(
        "clear-timezone-search"
      );
      const targetTimezonesSelect = document.getElementById("target_timezones");
      const timezoneCounter = document.getElementById("timezone-counter");

      if (timezoneSearchInput && targetTimezonesSelect) {
        // Armazenar todos os fusos horários originais para referência
        const allTimezones = [];
        const selectedTimezones = new Set();

        // Inicializar o array com todos os fusos horários e status de seleção
        for (let i = 0; i < targetTimezonesSelect.options.length; i++) {
          const option = targetTimezonesSelect.options[i];
          allTimezones.push({
            value: option.value,
            text: option.text,
            selected: option.selected,
          });

          if (option.selected) {
            selectedTimezones.add(option.value);
          }
        }

        // Atualizar contador inicialmente
        this.updateTimezoneCounter(
          timezoneCounter,
          allTimezones.length,
          allTimezones.length
        );

        // Evento para atualizar seleções
        targetTimezonesSelect.addEventListener("change", function () {
          // Atualizar o conjunto de fusos selecionados
          selectedTimezones.clear();
          for (let i = 0; i < this.options.length; i++) {
            if (this.options[i].selected) {
              selectedTimezones.add(this.options[i].value);
            }
          }
        });

        // Evento de busca
        timezoneSearchInput.addEventListener("input", () => {
          this.updateTimezoneList(
            timezoneSearchInput.value,
            allTimezones,
            selectedTimezones,
            targetTimezonesSelect,
            timezoneCounter
          );
        });

        // Clear search button
        if (clearTimezoneSearchBtn) {
          clearTimezoneSearchBtn.addEventListener("click", () => {
            timezoneSearchInput.value = "";
            this.updateTimezoneList(
              "",
              allTimezones,
              selectedTimezones,
              targetTimezonesSelect,
              timezoneCounter
            );
            timezoneSearchInput.focus();
          });
        }
      }
    },

    // Função para atualizar a lista de fusos com base no filtro
    updateTimezoneList: function (
      filter,
      allTimezones,
      selectedTimezones,
      targetSelect,
      counter
    ) {
      // Limpar o select atual
      targetSelect.innerHTML = "";

      // Filtrar os fusos horários
      const filteredTimezones =
        filter === ""
          ? allTimezones
          : allTimezones.filter((tz) =>
              tz.text.toLowerCase().includes(filter.toLowerCase())
            );

      // Adicionar as opções filtradas
      filteredTimezones.forEach((tz) => {
        const option = document.createElement("option");
        option.value = tz.value;
        option.text = tz.text;
        option.selected = selectedTimezones.has(tz.value);
        targetSelect.appendChild(option);
      });

      // Mostrar feedback se não houver resultados
      if (filteredTimezones.length === 0) {
        const noResults = document.createElement("option");
        noResults.disabled = true;
        noResults.text = "Nenhum fuso horário encontrado";
        targetSelect.appendChild(noResults);
      }

      // Atualizar contador de resultados
      this.updateTimezoneCounter(
        counter,
        filteredTimezones.length,
        allTimezones.length
      );
    },

    // Função para atualizar o contador de resultados
    updateTimezoneCounter: function (counterElement, count, total) {
      if (counterElement) {
        if (count === total) {
          counterElement.textContent = `Exibindo todos os ${total} fusos horários`;
        } else {
          counterElement.textContent = `Exibindo ${count} de ${total} fusos horários`;
        }
      }
    },
  };

  // Inicializar os utilitários de fuso horário
  TimeCalcTimezone.init();
});
