"use strict";

// The 3D layer reads relationships rendered from SQL. The component list and
// evidence pages remain the complete, usable reference without this module.
const openButton = document.querySelector("#visual-open");
const availability = document.querySelector("#visual-availability");
const experience = document.querySelector("#visual-experience");
const previewLayer = document.querySelector("#component-preview-layer");
const previewContent = document.querySelector("#component-preview-content");
const previewClose = document.querySelector("#component-preview-close");
const previewBackdrop = document.querySelector("#component-preview-backdrop");
let previewTrigger = null;

function closePreview() {
  if (!previewLayer || previewLayer.hidden) return;
  previewLayer.hidden = true;
  document.body.classList.remove("component-preview-open");
  previewContent.replaceChildren();
  if (previewTrigger?.isConnected) previewTrigger.focus();
  previewTrigger = null;
}

function openPreview(key, trigger) {
  if (!previewLayer || !previewContent) return false;
  const template = document.getElementById(`component-preview-${key}`);
  if (!(template instanceof HTMLTemplateElement)) return false;
  previewTrigger = trigger || document.activeElement;
  previewContent.replaceChildren(template.content.cloneNode(true));
  previewLayer.hidden = false;
  document.body.classList.add("component-preview-open");
  previewClose.focus();
  return true;
}

if (previewLayer) {
  for (const label of document.querySelectorAll(".diagram-node[data-component-preview-key] span")) {
    label.textContent = "Preview component here →";
  }
  previewClose.addEventListener("click", closePreview);
  previewBackdrop.addEventListener("click", closePreview);
  document.addEventListener("click", event => {
    const link = event.target.closest?.("a[data-component-preview-key]");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (link.target && link.target !== "_self") return;
    if (openPreview(link.dataset.componentPreviewKey, link)) event.preventDefault();
  });
  document.addEventListener("keydown", event => {
    if (previewLayer.hidden) return;
    if (event.key === "Escape") { event.preventDefault(); closePreview(); return; }
    if (event.key !== "Tab") return;
    const focusable = [...previewLayer.querySelectorAll("button:not([disabled]),a[href]")].filter(item => item.getClientRects().length);
    if (!focusable.length) return;
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
}

if (openButton && availability && experience) {
  let supported = false;
  try {
    const probe = document.createElement("canvas");
    const context = probe.getContext("webgl2");
    supported = Boolean(context);
    context?.getExtension("WEBGL_lose_context")?.loseContext();
  } catch (_) {
    supported = false;
  }

  if (supported) {
    openButton.hidden = false;
    let visual = null;
    openButton.addEventListener("click", async () => {
      if (visual) {
        experience.hidden = !experience.hidden;
        openButton.innerHTML = experience.hidden ? 'Explore in 3D <span aria-hidden="true">↗</span>' : 'Close 3D view <span aria-hidden="true">×</span>';
        if (!experience.hidden) visual.resize();
        return;
      }
      openButton.disabled = true;
      openButton.textContent = "Loading visual…";
      try {
        const THREE = await import("./vendor/three/three.module.js");
        experience.hidden = false;
        visual = createVisual(THREE, experience);
        visual.resize();
        openButton.innerHTML = 'Close 3D view <span aria-hidden="true">×</span>';
        availability.textContent = "";
      } catch (_) {
        experience.hidden = true;
        openButton.hidden = true;
        availability.textContent = "The 3D view is unavailable here. The component cards below still lead to every record.";
      } finally {
        openButton.disabled = false;
      }
    });
  } else {
    availability.textContent = "The 3D view is unavailable here. Use the component cards below.";
  }
}

function createVisual(THREE, root) {
  const host = root.querySelector("#visual-canvas");
  const stage = root.querySelector(".visual-stage");
  const picks = [...root.querySelectorAll(".visual-pick")];
  const callouts = [...root.querySelectorAll(".visual-callout")];
  const explodeButton = root.querySelector("#visual-explode");
  const explosionSlider = root.querySelector("#visual-explosion");
  const explosionValue = root.querySelector("#visual-explosion-value");
  const turnLeftButton = root.querySelector("#visual-turn-left");
  const turnRightButton = root.querySelector("#visual-turn-right");
  const resetButton = root.querySelector("#visual-reset");
  const name = root.querySelector("#visual-selected-name");
  const status = root.querySelector("#visual-selected-status");
  const scope = root.querySelector("#visual-selected-scope");
  const evidenceLink = root.querySelector("#visual-evidence-link");
  const componentLink = root.querySelector("#visual-component-link");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf1f7fa);
  const camera = new THREE.OrthographicCamera(-7, 7, 4.5, -4.5, 0.1, 100);
  let explosion = 0;
  let azimuth = 0.74;
  let elevation = 0.52;
  let distance = 17;
  function positionCamera() {
    camera.position.set(distance * Math.sin(azimuth) * Math.cos(elevation),
      distance * Math.sin(elevation), distance * Math.cos(azimuth) * Math.cos(elevation));
    camera.lookAt(0, 0.45 + explosion * 0.55, 0);
  }
  positionCamera();
  scene.add(new THREE.HemisphereLight(0xffffff, 0xb9c7cc, 2.2));
  const keyLight = new THREE.DirectionalLight(0xffffff, 2.8);
  keyLight.position.set(-4, 10, 8);
  scene.add(keyLight);
  const fillLight = new THREE.DirectionalLight(0xd9e7ff, 1.0);
  fillLight.position.set(5, 4, -6);
  scene.add(fillLight);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute("aria-hidden", "true");
  host.prepend(renderer.domElement);

  const boardMaterial = new THREE.MeshStandardMaterial({ color: 0x244753, metalness: 0.25, roughness: 0.62 });
  const boardEdge = new THREE.MeshStandardMaterial({ color: 0x16303b, metalness: 0.15, roughness: 0.8 });
  const goldMaterial = new THREE.MeshStandardMaterial({ color: 0xc4ad65, metalness: 0.65, roughness: 0.32 });
  const traceMaterial = new THREE.MeshStandardMaterial({ color: 0x5c8990, metalness: 0.25, roughness: 0.7 });
  const parts = new Map();

  function box(parent, width, height, depth, x, y, z, material) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
    mesh.position.set(x, y, z);
    parent.add(mesh);
    return mesh;
  }

  // These dimensions and placements are an intentionally generic diagram.
  // The cited packet establishes constituent descriptions, not board layout.
  const board = new THREE.Group();
  scene.add(board);
  // A recognizable M.2 silhouette, with an intentionally schematic contact
  // treatment. It does not assert a revision's pad count or board population.
  box(board, 8.1, 0.16, 2.4, -0.35, -0.14, 0, boardEdge);
  box(board, 0.7, 0.16, 1.35, 4.05, -0.14, -0.525, boardEdge);
  box(board, 0.7, 0.16, 0.6, 4.05, -0.14, 0.9, boardEdge);
  box(board, 8.0, 0.025, 2.27, -0.36, -0.045, 0, boardMaterial);
  box(board, 0.56, 0.025, 1.22, 4.04, -0.045, -0.525, goldMaterial);
  box(board, 0.56, 0.025, 0.48, 4.04, -0.045, 0.9, goldMaterial);
  for (const z of [-0.91, -0.67, 0.67, 0.91]) {
    box(board, 6.8, 0.009, 0.018, -0.6, -0.027, z, traceMaterial);
  }
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(1, 64),
    new THREE.MeshBasicMaterial({ color: 0x9db3bc, transparent: true, opacity: 0.22, depthWrite: false })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.scale.set(5.0, 1.6, 1);
  shadow.position.y = -0.53;
  scene.add(shadow);

  const templates = {
    "samsung-vnand-3bit": { x: -2.55, z: 0, width: 1.75, depth: 1.48, lift: 2.1, color: 0x2b4b5b },
    "samsung-phoenix": { x: 0.05, z: 0, width: 1.60, depth: 1.55, lift: 1.6, color: 0x1c394a },
    "samsung-lpddr4-512mb": { x: 2.48, z: 0, width: 1.29, depth: 1.20, lift: 1.05, color: 0x39586a }
  };

  function chipMark(label) {
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 256;
    const context = canvas.getContext("2d");
    context.fillStyle = "#587786";
    context.fillRect(0, 0, 512, 256);
    context.strokeStyle = "#9cb5bf";
    context.lineWidth = 3;
    context.strokeRect(18, 18, 476, 220);
    context.fillStyle = "#e9f4f5";
    context.font = "600 38px system-ui";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(label, 256, 128, 460);
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    return texture;
  }

  for (const pick of picks) {
    const partKey = pick.dataset.partKey;
    const template = templates[partKey];
    if (!template) throw new Error("Missing visual template for sourced part");
    const group = new THREE.Group();
    group.position.set(template.x, 0.19, template.z);
    scene.add(group);
    const material = new THREE.MeshStandardMaterial({ color: template.color, metalness: 0.2, roughness: 0.52 });
    const capMaterial = new THREE.MeshStandardMaterial({ color: 0x587786, metalness: 0.25, roughness: 0.45 });
    const markingMaterial = new THREE.MeshStandardMaterial({ map: chipMark(pick.dataset.partLabel), roughness: 0.55 });
    box(group, template.width, 0.3, template.depth, 0, 0, 0, material);
    box(group, template.width * 0.85, 0.012, template.depth * 0.77, 0, 0.158, 0,
      [capMaterial, capMaterial, markingMaterial, capMaterial, capMaterial, capMaterial]);
    group.traverse(object => { if (object.isMesh) object.userData.partKey = partKey; });
    parts.set(partKey, { group, template, material, capMaterial, markingMaterial });
  }

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let animationFrame = 0;

  function render() {
    positionCamera();
    renderer.render(scene, camera);
    for (const callout of callouts) {
      const part = parts.get(callout.dataset.calloutFor);
      if (!part) continue;
      const projected = part.group.position.clone();
      projected.y += 0.35;
      projected.project(camera);
      callout.style.left = `${(projected.x * 0.5 + 0.5) * 100}%`;
      callout.style.top = `${(-projected.y * 0.5 + 0.5) * 100}%`;
    }
  }

  function layout(progress) {
    for (const part of parts.values()) {
      part.group.position.set(
        part.template.x + progress * (part.template.x < 0 ? -0.45 : 0.32),
        0.19 + progress * part.template.lift,
        part.template.z + progress * (part.template.x < 0 ? -0.3 : 0.25)
      );
    }
    stage.classList.toggle("is-exploded", progress > 0.45);
    explosionSlider.value = String(Math.round(progress * 100));
    explosionValue.textContent = `${Math.round(progress * 100)}%`;
    render();
  }

  function setExplosion(target, animate = true) {
    cancelAnimationFrame(animationFrame);
    explodeButton.setAttribute("aria-pressed", String(target > 0.5));
    explodeButton.textContent = target > 0.5 ? "Assemble layers" : "Explode layers";
    if (!animate || reducedMotion.matches) {
      explosion = target;
      layout(explosion);
      return;
    }
    const start = explosion;
    const startTime = performance.now();
    function step(time) {
      const t = Math.min(1, (time - startTime) / 520);
      const eased = t * t * (3 - 2 * t);
      explosion = start + (target - start) * eased;
      layout(explosion);
      if (t < 1) animationFrame = requestAnimationFrame(step);
    }
    animationFrame = requestAnimationFrame(step);
  }

  function selectPart(key) {
    const pick = picks.find(item => item.dataset.partKey === key);
    for (const item of picks) item.setAttribute("aria-pressed", String(item === pick));
    for (const [partKey, part] of parts) {
      part.material.color.setHex(partKey === key ? 0xb7d843 : part.template.color);
      part.capMaterial.color.setHex(partKey === key ? 0xe0ee9a : 0x587786);
      part.markingMaterial.color.setHex(partKey === key ? 0xe0ee9a : 0xffffff);
    }
    if (pick) {
      name.textContent = pick.dataset.partName;
      status.textContent = `Contains · ${pick.dataset.assessment} · provisional`;
      scope.textContent = pick.dataset.scope;
      evidenceLink.href = pick.dataset.evidenceHref;
      componentLink.href = pick.dataset.componentHref;
      componentLink.dataset.componentPreviewKey = key;
      componentLink.textContent = "Preview component here →";
      evidenceLink.hidden = false;
      componentLink.hidden = false;
    } else {
      name.textContent = "Choose a part above or in the model.";
      status.textContent = "The visual is a guide to the existing record.";
      scope.textContent = "";
      delete componentLink.dataset.componentPreviewKey;
      evidenceLink.hidden = true;
      componentLink.hidden = true;
    }
    render();
  }

  for (const pick of picks) pick.addEventListener("click", () => {
    selectPart(pick.dataset.partKey);
    openPreview(pick.dataset.partKey, pick);
  });
  function pickedPart(event) {
    const bounds = renderer.domElement.getBoundingClientRect();
    pointer.set(((event.clientX - bounds.left) / bounds.width) * 2 - 1,
      -((event.clientY - bounds.top) / bounds.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects([...parts.values()].map(part => part.group), true)
      .find(item => item.object.userData.partKey);
    return hit?.object.userData.partKey;
  }
  let drag = null;
  renderer.domElement.addEventListener("pointerdown", event => {
    drag = { x: event.clientX, y: event.clientY, moved: false };
    renderer.domElement.setPointerCapture(event.pointerId);
  });
  renderer.domElement.addEventListener("pointermove", event => {
    if (!drag) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    drag.x = event.clientX;
    drag.y = event.clientY;
    if (Math.abs(dx) + Math.abs(dy) > 2) drag.moved = true;
    if (!drag.moved) return;
    azimuth -= dx * 0.008;
    elevation = Math.max(0.22, Math.min(1.05, elevation + dy * 0.006));
    render();
  });
  renderer.domElement.addEventListener("pointerup", event => {
    if (drag && !drag.moved) {
      const key = pickedPart(event);
      if (key) { selectPart(key); openPreview(key, openButton); }
    }
    drag = null;
  });
  renderer.domElement.addEventListener("pointercancel", () => { drag = null; });
  explosionSlider.addEventListener("input", () => setExplosion(Number(explosionSlider.value) / 100, false));
  explodeButton.addEventListener("click", () => setExplosion(explodeButton.getAttribute("aria-pressed") !== "true" ? 1 : 0));
  turnLeftButton.addEventListener("click", () => { azimuth -= Math.PI / 8; render(); });
  turnRightButton.addEventListener("click", () => { azimuth += Math.PI / 8; render(); });
  resetButton.addEventListener("click", () => {
    azimuth = 0.74;
    elevation = 0.52;
    distance = 17;
    setExplosion(0);
    selectPart(null);
  });
  renderer.domElement.addEventListener("webglcontextlost", event => {
    event.preventDefault();
    cancelAnimationFrame(animationFrame);
    root.hidden = true;
    openButton.hidden = true;
    availability.textContent = "The 3D view stopped working. The component cards below remain available.";
  });

  function resize() {
    if (root.hidden) return;
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height) return;
    const aspect = width / height;
    const halfHeight = Math.max(4.4, 6.1 / aspect);
    camera.left = -halfHeight * aspect;
    camera.right = halfHeight * aspect;
    camera.top = halfHeight;
    camera.bottom = -halfHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
    render();
  }
  new ResizeObserver(resize).observe(host);
  return { resize };
}
