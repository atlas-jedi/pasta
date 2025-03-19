/**
 * Gerenciamento de abas da Calculadora de Tempo
 */
document.addEventListener("DOMContentLoaded", function () {
  const TimeCalcTabs = {
    init: function () {
      this.setupMobileNavigation();
      this.setupTabEvents();
    },

    setupMobileNavigation: function () {
      // Configurar o menu mobile
      const mobileTabSelector = document.querySelector(".mobile-tab-selector");
      if (mobileTabSelector) {
        mobileTabSelector.addEventListener("change", function () {
          // Obter o valor selecionado
          const selectedTab = this.value;

          // Encontrar o botão da aba correspondente e simular o clique nele
          const tabButton = document.getElementById(selectedTab + "-tab");
          if (tabButton) {
            tabButton.click();
          }
        });

        // Verificar qual aba está ativa e selecionar a opção correspondente no dropdown
        const activeDesktopTab = document.querySelector(".nav-link.active");
        if (activeDesktopTab) {
          const activeTabId = activeDesktopTab.id.replace("-tab", "");
          mobileTabSelector.value = activeTabId;
        }
      }
    },

    setupTabEvents: function () {
      // Load timer content
      const timerTab = document.getElementById("timer-tab");
      if (timerTab) {
        timerTab.addEventListener("shown.bs.tab", function () {
          TimeCalcTabs.loadTabContent("timer", "time_calculator.timer");
        });
      }

      // Load stopwatch content
      const stopwatchTab = document.getElementById("stopwatch-tab");
      if (stopwatchTab) {
        stopwatchTab.addEventListener("shown.bs.tab", function () {
          TimeCalcTabs.loadTabContent("stopwatch", "time_calculator.stopwatch");
        });
      }
    },

    loadTabContent: function (tabId, endpointName) {
      const tabPane = document.getElementById(tabId);
      fetch(TimeCalcTabs.getUrl(endpointName), {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.text();
        })
        .then((html) => {
          console.log(`${tabId} content loaded successfully`);

          // Cria um elemento temporário para extrair o script sem executá-lo
          const tempDiv = document.createElement("div");
          tempDiv.innerHTML = html;

          // Encontra todos os scripts antes de inserir o HTML
          const scripts = Array.from(tempDiv.querySelectorAll("script")).map(
            (script) => {
              // Armazena o conteúdo e remove o script do HTML
              const content = script.textContent;
              const src = script.src;
              script.remove();
              return { content, src };
            }
          );

          // Insere o HTML sem os scripts
          tabPane.innerHTML = tempDiv.innerHTML;

          // Executa cada script após o HTML estar carregado
          scripts.forEach((scriptData) => {
            try {
              if (scriptData.src) {
                // Script externo
                const script = document.createElement("script");
                script.src = scriptData.src;
                document.body.appendChild(script);
              } else if (scriptData.content) {
                // Script inline
                const modifiedContent = scriptData.content
                  // Remove evento DOMContentLoaded e executa o código diretamente
                  .replace(
                    /document\.addEventListener\(['"]DOMContentLoaded['"], function\(\) \{([\s\S]*)\}\);/,
                    function (match, p1) {
                      return p1;
                    }
                  );

                // Executa o script modificado
                const script = document.createElement("script");
                script.textContent = `
                try {
                  ${modifiedContent}
                } catch(e) { 
                  console.error('Erro ao executar script do ${tabId}:', e);
                }
              `;
                document.body.appendChild(script);
                // Script inline pode ser removido após execução
                document.body.removeChild(script);
              }
            } catch (error) {
              console.error(`Erro ao processar script do ${tabId}:`, error);
            }
          });

          console.log(`${tabId} scripts executed`);
        })
        .catch((error) => {
          console.error(`Erro ao carregar ${tabId}:`, error);
          tabPane.innerHTML = `
          <div class="alert alert-danger">
            <h5>Erro ao carregar o ${
              tabId === "timer" ? "Timer" : "Cronômetro"
            }</h5>
            <p>Detalhes do erro: ${error.message}</p>
            <button class="btn btn-primary" onclick="location.reload()">Recarregar Página</button>
          </div>`;
        });
    },

    getUrl: function (endpointName) {
      // Extrair URL do template Flask usando uma abordagem adaptável
      // Este método depende da existência de meta tags ou uma função global
      // que forneça URLs para endpoints Flask

      // Suponha que temos um objeto window.flaskURLs que contém os endpoints
      if (window.flaskURLs && window.flaskURLs[endpointName]) {
        return window.flaskURLs[endpointName];
      }

      // Alternativa: buscar de elementos meta
      const metaURL = document.querySelector(`meta[name="${endpointName}"]`);
      if (metaURL) {
        return metaURL.getAttribute("content");
      }

      // Fallback para URL hardcoded (não recomendado, mas funcional)
      if (endpointName === "time_calculator.timer") {
        return "/time-calculator/timer";
      } else if (endpointName === "time_calculator.stopwatch") {
        return "/time-calculator/stopwatch";
      }

      // Se tudo falhar, tente uma URL relativa
      return `/${endpointName.replace(".", "/")}`;
    },
  };

  // Inicializar o gerenciador de abas
  TimeCalcTabs.init();
});
