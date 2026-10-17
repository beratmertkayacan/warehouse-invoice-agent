let current = null;

function element(id) {
  return document.getElementById(id);
}

function setText(id, text) {
  element(id).textContent = text;
}

function showError(message) {
  setText("error", message);
}

async function callApi(method, path, body) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }
  return data;
}

function fillList(id, items) {
  const list = element(id);
  list.replaceChildren();
  for (const item of items) {
    const row = document.createElement("li");
    row.textContent = item;
    list.append(row);
  }
}

function fillFields(fields) {
  const table = element("fields");
  table.replaceChildren();
  for (const [name, value] of Object.entries(fields)) {
    const row = table.insertRow();
    row.insertCell().textContent = name;
    row.insertCell().textContent = value ?? "-";
  }
}

function showApproval(status) {
  setText("approval", status ?? "No approval request");
  element("approve").hidden = status !== "pending";
  element("reject").hidden = status !== "pending";
  element("release").hidden = status === null;
}

function showResult(data) {
  current = data;
  element("result").hidden = false;
  setText("status", data.status);
  setText("answer", data.answer);
  fillFields(data.extractedFields);
  fillList("issues", data.validation.issues.length ? data.validation.issues : ["No issues"]);
  fillList("tools", data.toolCalls.map((call) => call.name));
  showApproval(data.approval ? data.approval.status : null);
  setText("release-result", "");
}

async function send() {
  showError("");
  element("send").disabled = true;
  try {
    const data = await callApi("POST", "/agent/chat", {
      sessionId: current?.sessionId,
      message: element("message").value,
    });
    showResult(data);
  } catch (error) {
    showError(error.message);
  } finally {
    element("send").disabled = false;
  }
}

async function decide(action) {
  showError("");
  try {
    const approval = await callApi("POST", `/approvals/${current.approval.id}/${action}`);
    showApproval(approval.status);
  } catch (error) {
    showError(error.message);
  }
}

async function release() {
  showError("");
  try {
    const shipment = await callApi("POST", `/shipments/${current.requestId}/release`);
    setText("release-result", `Released. Shipment ID: ${shipment.shipmentId}`);
  } catch (error) {
    showError(error.message);
  }
}

element("send").addEventListener("click", send);
element("approve").addEventListener("click", () => decide("approve"));
element("reject").addEventListener("click", () => decide("reject"));
element("release").addEventListener("click", release);
