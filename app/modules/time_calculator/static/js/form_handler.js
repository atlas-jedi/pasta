/**
 * Manipulação de formulários da Calculadora de Tempo
 */
document.addEventListener("DOMContentLoaded", function () {
  const TimeCalcForms = {
    init: function () {
      this.setupFormHandlers();
      this.setupDateToggleSwitches();
    },

    setupFormHandlers: function () {
      // Manipulador de formulários para envio via AJAX
      document.querySelectorAll(".ajax-form").forEach(function (form) {
        form.addEventListener("submit", function (e) {
          e.preventDefault(); // Previne o envio normal do formulário

          const formData = new FormData(this);
          // Adicionar parâmetro para solicitar resposta JSON
          formData.append("format", "json");

          const calculationType = formData.get("calculation_type");
          const tabId = this.closest(".tab-pane").id;
          const resultContainer = this.nextElementSibling;

          // Adicionar indicador de carregamento
          let loadingIndicator = document.createElement("div");
          loadingIndicator.className = "text-center mt-3";
          loadingIndicator.innerHTML =
            '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div><p class="mt-2">Calculando...</p>';

          // Se já existe um resultado, substituí-lo pelo indicador de carregamento
          if (resultContainer && resultContainer.classList.contains("alert")) {
            resultContainer.replaceWith(loadingIndicator);
          } else {
            // Caso contrário, adicionar o indicador após o formulário
            this.insertAdjacentElement("afterend", loadingIndicator);
          }

          // Enviar solicitação AJAX
          axios
            .post(this.action, formData)
            .then((response) => {
              // Verificar se a resposta é JSON
              const data = response.data;

              if (data.error) {
                loadingIndicator.replaceWith(
                  TimeCalcForms.createErrorElement(data.error)
                );
              } else {
                // Renderizar o resultado específico para cada tipo de cálculo
                let resultElement;

                switch (calculationType) {
                  case "add_subtract":
                    resultElement = TimeCalcForms.renderAddSubtractResult(data);
                    break;
                  case "difference":
                    resultElement = TimeCalcForms.renderDifferenceResult(data);
                    break;
                  case "convert_units":
                    resultElement = TimeCalcForms.renderConvertResult(data);
                    break;
                  case "divide_interval":
                    resultElement = TimeCalcForms.renderDivideResult(data);
                    break;
                  case "timezone_convert":
                    resultElement = TimeCalcForms.renderTimezoneResult(data);
                    break;
                  default:
                    resultElement = document.createElement("div");
                    resultElement.className = "alert alert-warning mt-4";
                    resultElement.textContent =
                      "Tipo de cálculo não suportado.";
                }

                if (resultElement) {
                  loadingIndicator.replaceWith(resultElement);
                } else {
                  loadingIndicator.innerHTML =
                    '<div class="alert alert-danger mt-3">Não foi possível processar o resultado.</div>';
                }
              }
            })
            .catch(function (error) {
              console.error("Erro ao calcular:", error);
              loadingIndicator.innerHTML =
                '<div class="alert alert-danger mt-3">Ocorreu um erro ao processar a solicitação.</div>';
            });
        });
      });
    },

    setupDateToggleSwitches: function () {
      // Date inclusion toggle for difference calculation
      const includeDateCheckbox = document.getElementById("include_date");
      if (includeDateCheckbox) {
        includeDateCheckbox.addEventListener("change", function () {
          TimeCalcForms.updateDateTimeInputs(
            "start_time_diff",
            "end_time_diff",
            this.checked
          );
        });
      }

      // Date inclusion toggle for interval division
      const includeDateIntervalCheckbox = document.getElementById(
        "include_date_interval"
      );
      if (includeDateIntervalCheckbox) {
        includeDateIntervalCheckbox.addEventListener("change", function () {
          TimeCalcForms.updateDateTimeInputs(
            "start_interval",
            "end_interval",
            this.checked
          );
        });
      }
    },

    // Função para atualizar inputs de data/hora com base no estado do checkbox
    updateDateTimeInputs: function (startId, endId, includeDate) {
      const startInput = document.getElementById(startId);
      const endInput = document.getElementById(endId);
      const startLabel = startInput.previousElementSibling;
      const endLabel = endInput.previousElementSibling;

      if (includeDate) {
        startInput.type = "datetime-local";
        endInput.type = "datetime-local";
        startLabel.textContent = "Data e Hora Inicial (YYYY-MM-DD HH:MM)";
        endLabel.textContent = "Data e Hora Final (YYYY-MM-DD HH:MM)";
        startInput.placeholder = "2023-01-01 09:00";
        endInput.placeholder = "2023-01-02 17:30";
      } else {
        startInput.type = "text";
        endInput.type = "text";
        startLabel.textContent = "Hora Inicial (HH:MM)";
        endLabel.textContent = "Hora Final (HH:MM)";
        startInput.placeholder = "09:00";
        endInput.placeholder = "17:30";
      }
    },

    // Funções para renderizar diferentes tipos de resultados
    createErrorElement: function (errorMessage) {
      const element = document.createElement("div");
      element.className = "mt-4 alert alert-danger";
      element.innerHTML = `<p>${errorMessage}</p>`;
      return element;
    },

    renderAddSubtractResult: function (data) {
      const element = document.createElement("div");
      element.className = "mt-4 alert alert-success";
      element.innerHTML = `
        <h5>Resultado:</h5>
        <p>A hora resultante é: <strong>${data.result_time}</strong></p>
      `;
      return element;
    },

    renderDifferenceResult: function (data) {
      const element = document.createElement("div");
      element.className = "mt-4 alert alert-success";
      element.innerHTML = `
        <h5>Resultado:</h5>
        <div class="row">
          <div class="col-md-6">
            <p class="mb-1">Formatado: <strong>${data.diff_hours} horas, ${data.diff_minutes} minutos e ${data.diff_seconds} segundos</strong></p>
          </div>
          <div class="col-md-6">
            <ul class="list-group">
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Segundos
                <span class="badge bg-primary rounded-pill">${data.total_seconds}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Minutos
                <span class="badge bg-primary rounded-pill">${data.total_minutes}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Horas
                <span class="badge bg-primary rounded-pill">${data.total_hours}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Dias
                <span class="badge bg-primary rounded-pill">${data.total_days}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Semanas
                <span class="badge bg-primary rounded-pill">${data.total_weeks}</span>
              </li>
            </ul>
          </div>
        </div>
      `;
      return element;
    },

    renderConvertResult: function (data) {
      const element = document.createElement("div");
      element.className = "mt-4 alert alert-success";
      element.innerHTML = `
        <h5>Resultado:</h5>
        <p>${data.value} ${data.from_unit} = <strong>${data.result} ${data.to_unit}</strong></p>
      `;
      return element;
    },

    renderDivideResult: function (data) {
      const intervalItems = data.intervals
        .map((interval, idx) => `<li class="list-group-item">${interval}</li>`)
        .join("");

      const element = document.createElement("div");
      element.className = "mt-4 alert alert-success";
      element.innerHTML = `
        <h5>Resultado:</h5>
        <p>Intervalo dividido em ${data.divisions} partes iguais de <strong>${data.division_duration}</strong> cada:</p>
        <ol class="list-group list-group-numbered">
          ${intervalItems}
        </ol>
      `;
      return element;
    },

    renderTimezoneResult: function (data) {
      const conversionRows = data.conversions
        .map(
          (conv) => `
        <tr>
          <td>${conv.timezone}</td>
          <td>${conv.time}</td>
          <td>${
            conv.dst_active
              ? '<i class="bi bi-check text-success"></i>'
              : '<i class="bi bi-x text-danger"></i>'
          }</td>
        </tr>
      `
        )
        .join("");

      const element = document.createElement("div");
      element.className = "mt-4 alert alert-success";
      element.innerHTML = `
        <h5>Resultado:</h5>
        <p>Hora em ${data.source_timezone}: <strong>${data.source_time}</strong></p>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Fuso Horário</th>
                <th>Hora</th>
                <th>Horário de Verão</th>
              </tr>
            </thead>
            <tbody>
              ${conversionRows}
            </tbody>
          </table>
        </div>
      `;
      return element;
    },
  };

  // Inicializar o manipulador de formulários
  TimeCalcForms.init();
});
