// import Two from 'two.js';
// import Zui from "two.js/extras/jsm/zui";

// export function addZUI(stage: Two, domElement: HTMLElement) {

//     var zui = new Zui.ZUI(undefined, domElement);
//     var mouse = new Two.Vector();
//     var touches = {};
//     var distance = 0;
//     var dragging = false;

//     zui.addLimits(0.06, 8);

//     domElement.addEventListener('mousedown', mousedown, false);
//     domElement.addEventListener('wheel', mousewheel, false);

//     function mousedown(e: MouseEvent) {
//       mouse.x = e.clientX;
//       mouse.y = e.clientY;
//       window.addEventListener('mousemove', mousemove, false);
//       window.addEventListener('mouseup', mouseup, false);
//     }

//     function mousemove(e: MouseEvent) {
//       var dx = e.clientX - mouse.x;
//       var dy = e.clientY - mouse.y;
//       zui.translateSurface(dx, dy);
//       mouse.set(e.clientX, e.clientY);
//     }

//     function mouseup(e: MouseEvent) {
//       window.removeEventListener('mousemove', mousemove, false);
//       window.removeEventListener('mouseup', mouseup, false);
//     }

//     function mousewheel(e: WheelEvent) {
//       var dy = (- e.deltaY) / 1000;
//       zui.zoomBy(dy, e.clientX, e.clientY);
//     }
// }