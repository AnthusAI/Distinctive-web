(function () {
  "use strict";

  var DISMISSED_STICKY_SIGNUP_KEY = "distinctive-sticky-signup-dismissed";
  var SHOWN_SLIDE_IN_KEY = "distinctive-slide-in-shown";
  var SUBSCRIBED_KEY = "distinctive-subscribed";
  var TOAST_VISIBLE_MILLISECONDS = 6000;

  function readStoredFlag(key) {
    try {
      return window.localStorage.getItem(key) === "1";
    } catch (storageUnavailable) {
      return false;
    }
  }

  function storeFlag(key) {
    try {
      window.localStorage.setItem(key, "1");
    } catch (storageUnavailable) {}
  }

  function fillTodaysDate() {
    var formattedToday = new Intl.DateTimeFormat("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" }).format(new Date());
    document.querySelectorAll("[data-ds-today]").forEach(function (element) {
      element.textContent = formattedToday;
    });
  }

  function pressOnly(buttons, chosenButton) {
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", button === chosenButton ? "true" : "false");
    });
  }

  function chosenFilterValue(container, filterName) {
    var pressed = container.querySelector('[data-ds-filter="' + filterName + '"][aria-pressed="true"]');
    return pressed ? pressed.getAttribute("data-ds-filter-value") : "all";
  }

  function wireFilterGroup(container, filterName, applyFilters) {
    var buttons = Array.prototype.slice.call(container.querySelectorAll('[data-ds-filter="' + filterName + '"]'));
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        pressOnly(buttons, button);
        applyFilters();
      });
    });
    var requestedValue = new URLSearchParams(window.location.search).get(filterName);
    if (requestedValue) {
      var requestedButton = buttons.find(function (button) {
        return button.getAttribute("data-ds-filter-value") === requestedValue;
      });
      if (requestedButton) pressOnly(buttons, requestedButton);
    }
  }

  function showSponsorRowsOnlyBetweenVisibleRows(rows) {
    var visibleRowSeen = false;
    rows.forEach(function (row) {
      if (row.getAttribute("data-ds-row") === "sponsor") {
        row.hidden = !visibleRowSeen;
      } else if (!row.hidden) {
        visibleRowSeen = true;
      }
    });
  }

  function setUpRulingFilters() {
    var container = document.querySelector("[data-ds-ruling-list]");
    if (!container) return;
    var rows = Array.prototype.slice.call(container.querySelectorAll("[data-ds-row]"));
    var countLabel = container.querySelector("[data-ds-count]");
    var emptyMessage = container.querySelector("[data-ds-empty]");

    function applyFilters() {
      var chosenIssue = chosenFilterValue(container, "issue");
      var chosenNotability = chosenFilterValue(container, "notability");
      var visibleRulingCount = 0;
      rows.forEach(function (row) {
        if (row.getAttribute("data-ds-row") !== "ruling") return;
        var matchesIssue = chosenIssue === "all" || row.getAttribute("data-ds-issue") === chosenIssue;
        var matchesNotability =
          chosenNotability === "all" ||
          (chosenNotability === "notable" && row.getAttribute("data-ds-notable") === "true") ||
          (chosenNotability === "precedential" && row.getAttribute("data-ds-precedential") === "true");
        row.hidden = !(matchesIssue && matchesNotability);
        if (!row.hidden) visibleRulingCount += 1;
      });
      showSponsorRowsOnlyBetweenVisibleRows(rows);
      if (countLabel) countLabel.textContent = visibleRulingCount === 1 ? "1 decision" : visibleRulingCount + " decisions";
      if (emptyMessage) emptyMessage.hidden = visibleRulingCount !== 0;
    }

    wireFilterGroup(container, "issue", applyFilters);
    wireFilterGroup(container, "notability", applyFilters);
    applyFilters();
  }

  function setUpWireFilters() {
    var container = document.querySelector("[data-ds-wire-list]");
    if (!container) return;
    var rows = Array.prototype.slice.call(container.querySelectorAll("[data-ds-row]"));
    var emptyMessage = container.querySelector("[data-ds-empty]");

    function applyFilters() {
      var chosenSource = chosenFilterValue(container, "source");
      var visibleItemCount = 0;
      rows.forEach(function (row) {
        if (row.getAttribute("data-ds-row") !== "wire") return;
        row.hidden = !(chosenSource === "all" || row.getAttribute("data-ds-source") === chosenSource);
        if (!row.hidden) visibleItemCount += 1;
      });
      showSponsorRowsOnlyBetweenVisibleRows(rows);
      if (emptyMessage) emptyMessage.hidden = visibleItemCount !== 0 || rows.length === 0;
    }

    wireFilterGroup(container, "source", applyFilters);
    applyFilters();
  }

  function showToast() {
    var toast = document.querySelector("[data-ds-toast]");
    if (!toast) return;
    toast.hidden = false;
    window.setTimeout(function () {
      toast.hidden = true;
    }, TOAST_VISIBLE_MILLISECONDS);
  }

  function signupPayload(form) {
    var formData = new FormData(form);
    return {
      email: formData.get("email"),
      lists: formData.getAll("lists"),
      topics: formData.getAll("topics"),
      page: window.location.pathname
    };
  }

  function showSubscribePageSuccess(form) {
    var formPanel = form.querySelector("[data-ds-subscribe-form]");
    var successPanel = form.querySelector("[data-ds-subscribe-success]");
    if (formPanel && successPanel) {
      formPanel.hidden = true;
      successPanel.hidden = false;
      return true;
    }
    return false;
  }

  function setFormStatus(form, message) {
    var status = form.querySelector("[data-ds-form-status]");
    if (status) {
      status.textContent = message;
    } else if (message) {
      window.alert(message);
    }
  }

  function setUpSignupForms() {
    var requestedEmail = new URLSearchParams(window.location.search).get("email");
    document.querySelectorAll("[data-ds-signup]").forEach(function (form) {
      var isSubscribePage = form.hasAttribute("data-ds-subscribe-page");
      if (isSubscribePage && requestedEmail) {
        var emailInput = form.querySelector('input[name="email"]');
        if (emailInput) emailInput.value = requestedEmail;
      }
      var resetButton = form.querySelector("[data-ds-subscribe-reset]");
      if (resetButton) {
        resetButton.addEventListener("click", function () {
          form.querySelector("[data-ds-subscribe-form]").hidden = false;
          form.querySelector("[data-ds-subscribe-success]").hidden = true;
          form.reset();
        });
      }
      form.addEventListener("submit", function (event) {
        if (form.method.toLowerCase() !== "post") {
          if (isSubscribePage) {
            event.preventDefault();
            setFormStatus(form, "Signups for The Docket open soon. Your address was not saved.");
          }
          return;
        }
        event.preventDefault();
        setFormStatus(form, "");
        fetch(form.action, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(signupPayload(form))
        })
          .then(function (response) {
            if (!response.ok) throw new Error("Signup failed with status " + response.status);
            storeFlag(SUBSCRIBED_KEY);
            if (!showSubscribePageSuccess(form)) {
              form.reset();
              showToast();
            }
          })
          .catch(function () {
            setFormStatus(form, "Something went wrong. Please try again in a moment.");
          });
      });
    });
  }

  function setUpStickySignupBar() {
    var stickyBar = document.querySelector("[data-ds-sticky-signup]");
    var articleBody = document.querySelector(".ds-prose");
    if (!stickyBar || !articleBody || readStoredFlag(DISMISSED_STICKY_SIGNUP_KEY) || readStoredFlag(SUBSCRIBED_KEY)) return;
    function revealAfterHalfTheArticle() {
      var bodyBounds = articleBody.getBoundingClientRect();
      var halfwayPoint = bodyBounds.top + bodyBounds.height / 2;
      if (halfwayPoint < window.innerHeight) {
        stickyBar.hidden = false;
        window.removeEventListener("scroll", revealAfterHalfTheArticle);
      }
    }
    window.addEventListener("scroll", revealAfterHalfTheArticle, { passive: true });
    stickyBar.querySelector('[data-ds-dismiss="sticky-signup"]').addEventListener("click", function () {
      stickyBar.hidden = true;
      storeFlag(DISMISSED_STICKY_SIGNUP_KEY);
    });
  }

  function setUpExitIntentSlideIn() {
    var slideIn = document.querySelector("[data-ds-slide-in]");
    var finePointer = window.matchMedia && window.matchMedia("(pointer: fine)").matches;
    if (!slideIn || !finePointer || readStoredFlag(SHOWN_SLIDE_IN_KEY) || readStoredFlag(SUBSCRIBED_KEY)) return;
    function showOnExitIntent(event) {
      if (event.relatedTarget || event.clientY > 0) return;
      var stickyBar = document.querySelector("[data-ds-sticky-signup]");
      if (stickyBar) stickyBar.hidden = true;
      slideIn.hidden = false;
      storeFlag(SHOWN_SLIDE_IN_KEY);
      document.removeEventListener("mouseout", showOnExitIntent);
    }
    document.addEventListener("mouseout", showOnExitIntent);
    slideIn.querySelector('[data-ds-dismiss="slide-in"]').addEventListener("click", function () {
      slideIn.hidden = true;
    });
  }

  function start() {
    fillTodaysDate();
    setUpRulingFilters();
    setUpWireFilters();
    setUpSignupForms();
    setUpStickySignupBar();
    setUpExitIntentSlideIn();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
