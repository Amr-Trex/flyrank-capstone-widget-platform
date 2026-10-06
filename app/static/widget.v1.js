(function () {
  function log() {
    if (window.console && console.log) {
      console.log.apply(console, arguments);
    }
  }

  var script = document.currentScript;

  if (!script) {
    log("[widget] Could not find currentScript");
    return;
  }

  var scriptUrl = new URL(script.src);
  var widgetId = scriptUrl.searchParams.get("id");
  var apiOrigin = scriptUrl.origin;

  if (!widgetId) {
    log("[widget] Missing widget id");
    return;
  }

  log("[widget] loading", widgetId);

  var mount = document.createElement("div");
  mount.className = "flyrank-widget-mount";
  script.parentNode.insertBefore(mount, script);

  fetch(apiOrigin + "/public/widgets/" + encodeURIComponent(widgetId) + "/config")
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Config request failed with " + response.status);
      }

      return response.json();
    })
    .then(function (config) {
      renderWidget(mount, config, widgetId);
      log("[widget] rendered", widgetId);
    })
    .catch(function (error) {
      mount.textContent = "Widget unavailable";
      log("[widget] error", error);
    });

  function renderWidget(mount, config, widgetId) {
    mount.innerHTML = "";

    var form = document.createElement("form");
    form.style.border = "1px solid #ddd";
    form.style.borderRadius = "8px";
    form.style.padding = "16px";
    form.style.maxWidth = "360px";
    form.style.fontFamily = "sans-serif";

    var title = document.createElement("h3");
    title.textContent = config.title || "Subscribe";
    title.style.marginTop = "0";
    form.appendChild(title);

    if (config.description) {
      var description = document.createElement("p");
      description.textContent = config.description;
      form.appendChild(description);
    }

    (config.fields || []).forEach(function (field) {
      var label = document.createElement("label");
      label.style.display = "block";
      label.style.marginBottom = "10px";
      label.textContent = field.label || field.name;

      var input;

      if (field.type === "textarea") {
        input = document.createElement("textarea");
      } else {
        input = document.createElement("input");
        input.type = field.type || "text";
      }

      input.name = field.name;

      if (field.required) {
        input.required = true;
      }

      input.style.display = "block";
      input.style.width = "100%";
      input.style.padding = "8px";
      input.style.marginTop = "4px";
      input.style.boxSizing = "border-box";

      label.appendChild(input);
      form.appendChild(label);
    });

    var honeypot = document.createElement("input");
    honeypot.type = "text";
    honeypot.name = config.honeypot_field || "website";
    honeypot.style.display = "none";
    honeypot.tabIndex = -1;
    honeypot.autocomplete = "off";
    form.appendChild(honeypot);

    var button = document.createElement("button");
    button.type = "submit";
    button.textContent = config.button_text || "Submit";
    button.style.padding = "10px 14px";
    form.appendChild(button);

    var message = document.createElement("p");
    message.style.marginBottom = "0";
    form.appendChild(message);

    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var formData = new FormData(form);
      var data = {};

      formData.forEach(function (value, key) {
        data[key] = value;
      });

      var payload = {
        widget_public_id: widgetId,
        data: data,
      };

      button.disabled = true;
      message.textContent = "Submitting...";

      fetch(config.submit_url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then(function (response) {
          if (response.status === 201 || response.status === 200) {
            message.textContent = "Thank you! Your submission was received.";
            log("[widget] submitted", widgetId);
            form.reset();
            return;
          }

          return response.json().then(function (body) {
            throw new Error(body.detail || "Request failed with " + response.status);
          });
        })
        .catch(function (error) {
          message.textContent = "Submission failed. Please try again.";
          log("[widget] submission failed", error);
          button.disabled = false;
        });
    });

    mount.appendChild(form);
  }
})();