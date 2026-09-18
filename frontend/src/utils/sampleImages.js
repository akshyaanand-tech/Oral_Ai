/**
 * Helper to generate synthetic dental demo images as JPEG Blobs for instant testing.
 */

function createDentalCanvas(view, isBlurry = false) {
  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = 480;
  const ctx = canvas.getContext('2d');

  if (isBlurry) {
    ctx.filter = 'blur(4.5px)';
  }

  // Background
  const grad = ctx.createLinearGradient(0, 0, 0, 480);
  grad.addColorStop(0, '#1e293b');
  grad.addColorStop(1, '#0f172a');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 640, 480);

  // Oral cavity backdrop
  ctx.fillStyle = '#450a0a';
  ctx.beginPath();
  ctx.ellipse(320, 240, 240, 160, 0, 0, Math.PI * 2);
  ctx.fill();

  // Gum arches
  ctx.fillStyle = '#be123c';
  ctx.beginPath();
  ctx.ellipse(320, 160, 200, 70, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.beginPath();
  ctx.ellipse(320, 320, 190, 65, 0, 0, Math.PI * 2);
  ctx.fill();

  // Draw teeth
  ctx.fillStyle = '#f8fafc';
  ctx.strokeStyle = '#94a3b8';
  ctx.lineWidth = 2;

  // Upper arch teeth
  const upperTeeth = 8;
  for (let i = 0; i < upperTeeth; i++) {
    const x = 160 + i * 40;
    const y = 180 + Math.sin((i / (upperTeeth - 1)) * Math.PI) * 20;
    ctx.beginPath();
    ctx.roundRect(x, y, 32, 42, [6, 6, 3, 3]);
    ctx.fill();
    ctx.stroke();
  }

  // Lower arch teeth
  const lowerTeeth = 8;
  for (let i = 0; i < lowerTeeth; i++) {
    const x = 170 + i * 38;
    const y = 250 - Math.sin((i / (lowerTeeth - 1)) * Math.PI) * 15;
    ctx.beginPath();
    ctx.roundRect(x, y, 30, 40, [3, 3, 6, 6]);
    ctx.fill();
    ctx.stroke();
  }

  // View specific annotations and features
  ctx.fillStyle = isBlurry ? '#f43f5e' : '#38bdf8';
  ctx.font = 'bold 20px sans-serif';
  ctx.fillText(`DEMO ${view.toUpperCase()} VIEW ${isBlurry ? '(BLURRY DEMO)' : ''}`, 30, 50);

  ctx.fillStyle = '#94a3b8';
  ctx.font = '14px sans-serif';
  ctx.fillText(isBlurry ? 'Soft focus simulation for AI Enhancement testing' : 'High-resolution calibrated test image', 30, 80);

  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(blob);
    }, 'image/jpeg', 0.92);
  });
}

export async function getSampleDentalImage(view) {
  return await createDentalCanvas(view, false);
}

export async function getBlurrySampleDentalImage(view) {
  return await createDentalCanvas(view, true);
}

export async function getAllSampleDentalImages() {
  const views = ['front', 'left', 'right', 'upper', 'lower'];
  const result = {};
  for (const v of views) {
    result[v] = await createDentalCanvas(v, false);
  }
  return result;
}

