let graphId = null;

const result = document.querySelector("#result");
const vertexCount = document.querySelector("#vertexCount");
const edgeCount = document.querySelector("#edgeCount");
const cycleState = document.querySelector("#cycleState");

function show(payload) {
  result.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
}

function updateGraphSummary(graph) {
  vertexCount.textContent = graph.vertex_count;
  edgeCount.textContent = graph.edge_count;
  cycleState.textContent = graph.has_cycle ? "Has" : "No";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    throw new Error(payload.detail || response.statusText);
  }
  return payload;
}

async function ensureGraph() {
  if (graphId) return graphId;
  const graph = await api("/graphs", {
    method: "POST",
    body: JSON.stringify({ name: "dashboard-network" }),
  });
  graphId = graph.id;
  updateGraphSummary(graph);
  show(graph);
  return graphId;
}

document.querySelector("#createGraph").addEventListener("click", async () => {
  graphId = null;
  await ensureGraph();
});

document.querySelector("#vertexForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = await ensureGraph();
  const graph = await api(`/graphs/${id}/vertices`, {
    method: "POST",
    body: JSON.stringify({ id: document.querySelector("#vertexId").value }),
  });
  updateGraphSummary(graph);
  show(graph);
});

document.querySelector("#edgeForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = await ensureGraph();
  const graph = await api(`/graphs/${id}/edges`, {
    method: "POST",
    body: JSON.stringify({
      source: document.querySelector("#edgeSource").value,
      destination: document.querySelector("#edgeDestination").value,
      cost: Number(document.querySelector("#edgeCost").value),
      distance: Number(document.querySelector("#edgeDistance").value),
      travel_time: Number(document.querySelector("#edgeTime").value),
    }),
  });
  updateGraphSummary(graph);
  show(graph);
});

document.querySelector("#routeForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = await ensureGraph();
  const route = await api(`/graphs/${id}/routes/shortest`, {
    method: "POST",
    body: JSON.stringify({
      source: document.querySelector("#routeSource").value,
      destination: document.querySelector("#routeDestination").value,
      optimise_for: document.querySelector("#routeMetric").value,
    }),
  });
  show(route);
});

ensureGraph().catch((error) => show(error.message));
