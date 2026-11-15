function buildRiskCard() {
      var state = {
        o2: 32,
        pressure: 101.3,
        gravity: 0,
        airflow: 'mild',
        material: 'nomex',
        ignition: 'low',
        occupancy: 'medium',
        phase: 'transit',
        suppression: 'good',
        toxicity: 'moderate'
      };

      var refs = {};
      var scoreValue = h('span', { class: 'risk-score-value', text: '3' });
      var scoreLabel = h('span', { class: 'risk-score-label sev-caution', text: 'LIKELIHOOD 3' });
      var summary = h('p', { class: 'risk-summary', text: 'Likelihood × Severity matrix: monitor oxygen-rich and low-pressure transitions.' });
      var bucket = h('span', { class: 'risk-bucket', text: 'MEDIUM' });
      var flameStateLabel = h('span', { class: 'flame-state', text: 'TRANSITIONAL PLUME' });
      var flameCase = h('span', { class: 'flame-case', text: 'CREW CASE · HSE MEDIUM' });
      var flameDescription = h('p', { class: 'flame-description', text: '' });
      var flameDrivers = h('div', { class: 'flame-drivers' });
      var svgNamespace = 'http://www.w3.org/2000/svg';

      function svgNode(tag, attrs, children) {
        var node = document.createElementNS(svgNamespace, tag);
        Object.keys(attrs || {}).forEach(function (key) { node.setAttribute(key, attrs[key]); });
        (children || []).forEach(function (child) { if (child) node.appendChild(child); });
        return node;
      }

      var flameOutline = svgNode('path', { class: 'flame-outline', d: '' });
      var flameCore = svgNode('path', { class: 'flame-core', d: '' });
      var flameSvg = svgNode('svg', { viewBox: '0 0 260 220', role: 'img', 'aria-label': 'Illustrative flame morphology based on selected factors' }, [
        svgNode('defs', {}, [
          svgNode('linearGradient', { id: 'flameBodyGradient', x1: '0', y1: '1', x2: '0', y2: '0' }, [
            svgNode('stop', { offset: '0%', 'stop-color': '#f97316', 'stop-opacity': '0.5' }),
            svgNode('stop', { offset: '55%', 'stop-color': '#fb923c', 'stop-opacity': '0.88' }),
            svgNode('stop', { offset: '100%', 'stop-color': '#fde68a', 'stop-opacity': '0.95' })
          ]),
          svgNode('linearGradient', { id: 'flameCoreGradient', x1: '0', y1: '1', x2: '0', y2: '0' }, [
            svgNode('stop', { offset: '0%', 'stop-color': '#fbbf24', 'stop-opacity': '0.18' }),
            svgNode('stop', { offset: '100%', 'stop-color': '#fff7ed', 'stop-opacity': '0.9' })
          ])
        ]),
        svgNode('line', { class: 'flame-air-arrow', x1: '18', y1: '48', x2: '60', y2: '48', opacity: '0' }),
        svgNode('polygon', { class: 'flame-air-arrow-head', points: '60,48 50,42 50,54', opacity: '0' }),
        flameOutline,
        flameCore,
        svgNode('line', { class: 'flame-ground', x1: '64', y1: '198', x2: '196', y2: '198' }),
        svgNode('rect', { class: 'flame-source', x: '119', y: '188', width: '22', height: '10', rx: '2' })
      ]);

      var fieldRows = [
        { key: 'o2', label: 'O₂ %', type: 'number', min: 15, max: 40, step: 0.5, value: state.o2 },
        { key: 'pressure', label: 'Pressure', type: 'number', min: 40, max: 140, step: 1, value: state.pressure },
        { key: 'gravity', label: 'Gravity (m/s²)', type: 'number', min: 0, max: 16, step: 0.1, value: state.gravity }
      ].map(function (spec) {
        var input = h('input', {
          type: spec.type,
          min: String(spec.min),
          max: String(spec.max),
          step: String(spec.step),
          value: String(spec.value),
          'aria-label': spec.label
        });
        refs[spec.key] = input;
        return h('div', { class: 'risk-field' }, [
          h('label', { text: spec.label }),
          input
        ]);
      });

      var selects = [
        { key: 'material', label: 'Material', options: [
          ['nomex', 'Nomex'],
          ['kapton', 'Kapton'],
          ['cotton', 'Cotton batting'],
          ['pmma', 'PMMA'],
          ['silicone', 'Silicone']
        ], value: state.material },
        { key: 'airflow', label: 'Airflow', options: [
          ['still', 'Still'],
          ['mild', 'Mild'],
          ['high', 'High'],
          ['fan', 'Forced flow']
        ], value: state.airflow },
        { key: 'ignition', label: 'Ignition', options: [
          ['none', 'None'],
          ['low', 'Low'],
          ['medium', 'Medium'],
          ['high', 'High']
        ], value: state.ignition },
        { key: 'occupancy', label: 'Crew occupancy', options: [
          ['low', 'Low'],
          ['medium', 'Medium'],
          ['high', 'High']
        ], value: state.occupancy },
        { key: 'phase', label: 'Mission phase', options: [
          ['transit', 'Transit'],
          ['surface', 'Surface ops'],
          ['eva', 'EVA'],
          ['launch', 'Launch/abort']
        ], value: state.phase },
        { key: 'suppression', label: 'Suppression', options: [
          ['good', 'Good'],
          ['limited', 'Limited'],
          ['none', 'None']
        ], value: state.suppression }
      ].map(function (spec) {
        var select = h('select', { 'aria-label': spec.label }, spec.options.map(function (opt) {
          return h('option', { value: opt[0], text: opt[1] });
        }));
        select.value = spec.value;
        refs[spec.key] = select;
        return h('div', { class: 'risk-field' }, [
          h('label', { text: spec.label }),
          select
        ]);
      });

      var matrix = h('div', { class: 'risk-matrix' });
      var axisLabels = ['1', '2', '3', '4', '5'];
      var riskLabels = ['Low', 'Medium', 'High', 'Critical'];
      var matrixCells = [];

      function drawMatrix() {
        matrix.textContent = '';
        var cellMap = {};
        for (var r = 0; r <= 5; r++) {
          for (var c = 0; c <= 5; c++) {
            if (r === 0 && c === 0) {
              matrix.appendChild(h('div', { class: 'risk-matrix-head', text: '' }));
              continue;
            }
            if (r === 0) {
              matrix.appendChild(h('div', { class: 'risk-matrix-head', text: axisLabels[c - 1] }));
              continue;
            }
            if (c === 0) {
              matrix.appendChild(h('div', { class: 'risk-matrix-label', text: String(r) }));
              continue;
            }
            var cell = h('div', { class: 'risk-matrix-cell', text: '' });
            matrix.appendChild(cell);
            cellMap[(r - 1) + ':' + (c - 1)] = cell;
          }
        }
        return cellMap;
      }

      var matrixMap = drawMatrix();
      var cellsByIndex = Object.keys(matrixMap).reduce(function (out, key) {
        out[key] = matrixMap[key];
        return out;
      }, {});

      function clamp(value, min, max) { return Math.min(max, Math.max(min, value)); }

      function scoreLikelihood(data) {
        var o2 = clamp((data.o2 - 17) / (30 - 17), 0, 1);
        var pressure = data.pressure < 80 ? 1 : data.pressure < 100 ? 0.6 : 0.2;
        var gravityG = data.gravity / 9.81;
        var gravity = gravityG <= 0.1 ? 0.9 : gravityG < 1 ? 0.7 : 0.2;
        var material = { nomex: 0.35, kapton: 0.5, cotton: 0.8, pmma: 0.9, silicone: 0.3 }[data.material] || 0.4;
        var ignition = { none: 0.0, low: 0.3, medium: 0.6, high: 0.9 }[data.ignition] || 0.2;
        var airflow = { still: 0.2, mild: 0.45, high: 0.7, fan: 0.85 }[data.airflow] || 0.3;

        var weighted = 0.35 * (o2 * 10) + 0.15 * (pressure * 10) + 0.10 * (gravity * 10) + 0.20 * (material * 10) + 0.10 * (ignition * 10) + 0.10 * (airflow * 10);
        return clamp(weighted, 0, 10);
      }

      function scoreSeverity(data) {
        var occupancy = { low: 2, medium: 5, high: 9 }[data.occupancy] || 4;
        var phase = { transit: 4, surface: 6, eva: 8, launch: 9 }[data.phase] || 5;
        var suppression = { good: 2, limited: 5, none: 9 }[data.suppression] || 4;
        var toxicity = { low: 2, moderate: 5, high: 8 }[data.toxicity] || 4;
        var criticality = { low: 2, medium: 5, high: 8 }[data.criticality] || 5;

        var weighted = 0.28 * occupancy + 0.22 * phase + 0.20 * suppression + 0.15 * toxicity + 0.15 * criticality;
        return clamp(weighted, 0, 10);
      }

      function riskBucketFromScores(likelihood, severity) {
        var product = Math.round((likelihood / 10) * 5) * Math.round((severity / 10) * 5);
        var v = clamp(product, 1, 25);
        if (v <= 4) return { label: 'LOW', bucket: 'low', color: '#34d399' };
        if (v <= 9) return { label: 'MEDIUM', bucket: 'medium', color: '#fbbf24' };
        if (v <= 16) return { label: 'HIGH', bucket: 'high', color: '#f97316' };
        return { label: 'CRITICAL', bucket: 'critical', color: '#f43f5e' };
      }

      function readNumericInput(key) {
        var input = refs[key];
        var min = Number(input.min);
        var max = Number(input.max);
        var value = Number(input.value);
        if (!isFinite(value)) value = min;
        value = clamp(value, min, max);
        if (Number(input.value) !== value) input.value = String(value);
        return value;
      }

      function updateFlameBehavior(bucketInfo, likelihoodLevel, severityLevel) {
        var gravityG = state.gravity / 9.81;
        var gravityRatio = clamp(gravityG / 1.6, 0, 1);
        var airStrength = { still: 0, mild: 0.18, high: 0.58, fan: 0.9 }[state.airflow] || 0;
        var materialFactor = { nomex: 0.68, kapton: 0.78, cotton: 0.95, pmma: 1, silicone: 0.64 }[state.material] || 0.7;
        var ignitionFactor = { none: 0, low: 0.42, medium: 0.72, high: 1 }[state.ignition] || 0.4;
        var suppressionFactor = { good: 0.58, limited: 0.82, none: 1 }[state.suppression] || 0.7;
        var oxygenFactor = clamp(state.o2 / 30, 0.35, 1.35);
        var pressureFactor = clamp(state.pressure / 101.3, 0.65, 1.25);
        var intensity = clamp(materialFactor * ignitionFactor * suppressionFactor * oxygenFactor * pressureFactor, 0, 1.25);
        var width = 14 + 31 * intensity;
        var height = 50 + 64 * intensity + 42 * gravityRatio;
        var lean = airStrength * (12 + gravityRatio * 34);
        var outline = '';
        var core = '';
        var stateText;
        var description;

        if (state.ignition === 'none') {
          stateText = 'NO IGNITION INPUT';
          description = 'The selected inputs specify no ignition source. This is a scenario assumption, not a guarantee that a fire cannot occur.';
        } else if (gravityG <= 0.1) {
          var radiusX = 18 + 30 * intensity;
          var radiusY = 20 + 31 * intensity;
          var centerX = 130 + airStrength * 20;
          var centerY = 153;
          outline = 'M ' + centerX + ' ' + (centerY - radiusY) +
            ' C ' + (centerX + radiusX * 0.55) + ' ' + (centerY - radiusY) + ' ' + (centerX + radiusX) + ' ' + (centerY - radiusY * 0.55) + ' ' + (centerX + radiusX) + ' ' + centerY +
            ' C ' + (centerX + radiusX) + ' ' + (centerY + radiusY * 0.55) + ' ' + (centerX + radiusX * 0.55) + ' ' + (centerY + radiusY) + ' ' + centerX + ' ' + (centerY + radiusY) +
            ' C ' + (centerX - radiusX * 0.55) + ' ' + (centerY + radiusY) + ' ' + (centerX - radiusX) + ' ' + (centerY + radiusY * 0.55) + ' ' + (centerX - radiusX) + ' ' + centerY +
            ' C ' + (centerX - radiusX) + ' ' + (centerY - radiusY * 0.55) + ' ' + (centerX - radiusX * 0.55) + ' ' + (centerY - radiusY) + ' ' + centerX + ' ' + (centerY - radiusY) + ' Z';
          core = 'M ' + centerX + ' ' + (centerY - radiusY * 0.55) +
            ' C ' + (centerX + radiusX * 0.38) + ' ' + (centerY - radiusY * 0.55) + ' ' + (centerX + radiusX * 0.48) + ' ' + (centerY + radiusY * 0.15) + ' ' + centerX + ' ' + (centerY + radiusY * 0.54) +
            ' C ' + (centerX - radiusX * 0.48) + ' ' + (centerY + radiusY * 0.15) + ' ' + (centerX - radiusX * 0.38) + ' ' + (centerY - radiusY * 0.55) + ' ' + centerX + ' ' + (centerY - radiusY * 0.55) + ' Z';
          stateText = airStrength > 0.55 ? 'LOW-G · FLOW-DISTORTED ENVELOPE' : 'LOW-G · ROUNDED ENVELOPE';
          description = 'At near-zero gravity, buoyant rise is weak, so the illustration is rounded around the source. Airflow can still displace or distort it.';
        } else {
          var apexX = 130 + lean;
          var baseY = 196;
          var tipY = Math.max(34, baseY - height);
          outline = 'M 130 ' + baseY +
            ' C ' + (130 - width) + ' ' + (baseY - height * 0.24) + ' ' + (apexX - width * 0.58) + ' ' + (baseY - height * 0.72) + ' ' + apexX + ' ' + tipY +
            ' C ' + (apexX + width * 0.58) + ' ' + (baseY - height * 0.72) + ' ' + (130 + width) + ' ' + (baseY - height * 0.24) + ' 130 ' + baseY + ' Z';
          core = 'M 130 ' + baseY +
            ' C ' + (130 - width * 0.36) + ' ' + (baseY - height * 0.24) + ' ' + (apexX - width * 0.2) + ' ' + (baseY - height * 0.69) + ' ' + apexX + ' ' + (tipY + 9) +
            ' C ' + (apexX + width * 0.2) + ' ' + (baseY - height * 0.69) + ' ' + (130 + width * 0.36) + ' ' + (baseY - height * 0.24) + ' 130 ' + baseY + ' Z';
          stateText = airStrength > 0.55 ? 'BUOYANT PLUME · FORCED-FLOW LEAN' : gravityRatio > 0.55 ? 'BUOYANCY-LIFTED PLUME' : 'TRANSITIONAL PLUME';
          description = 'Increasing gravity strengthens buoyant rise and elongates the plume. Cross-flow adds a qualitative downwind lean; pressure, oxygen, fuel, ignition and suppression scale the sketch.';
        }

        flameOutline.setAttribute('d', outline);
        flameCore.setAttribute('d', core);
        flameOutline.style.opacity = state.ignition === 'none' ? '0.08' : String(clamp(0.35 + intensity * 0.5, 0.3, 1));
        flameCore.style.opacity = state.ignition === 'none' ? '0' : String(clamp(intensity, 0.15, 0.95));
        var arrowLine = flameSvg.querySelector('.flame-air-arrow');
        var arrowHead = flameSvg.querySelector('.flame-air-arrow-head');
        var arrowEnd = 18 + airStrength * 76;
        arrowLine.setAttribute('x2', String(arrowEnd));
        arrowLine.setAttribute('opacity', String(airStrength > 0 ? 0.78 : 0));
        arrowHead.setAttribute('points', arrowEnd + ',48 ' + (arrowEnd - 10) + ',42 ' + (arrowEnd - 10) + ',54');
        arrowHead.setAttribute('opacity', String(airStrength > 0 ? 0.78 : 0));
        flameStateLabel.textContent = stateText;
        flameDescription.textContent = description;
        flameDrivers.textContent = '';
        [
          gravityG.toFixed(2) + ' g · ' + state.gravity.toFixed(1) + ' m/s²',
          'Pressure: ' + state.pressure.toFixed(1) + ' kPa',
          'Airflow: ' + state.airflow,
          'O₂: ' + state.o2 + '%',
          'Fuel: ' + state.material,
          'Suppression: ' + state.suppression
        ].forEach(function (label) { flameDrivers.appendChild(h('span', { text: label })); });
        flameCase.textContent = 'CREW INPUTS · HSE ' + bucketInfo.label + ' · L' + likelihoodLevel + ' × S' + severityLevel;
      }

      function updateRisk() {
        state.o2 = readNumericInput('o2');
        state.pressure = readNumericInput('pressure');
        state.gravity = readNumericInput('gravity');
        state.material = refs.material.value;
        state.airflow = refs.airflow.value;
        state.ignition = refs.ignition.value;
        state.occupancy = refs.occupancy.value;
        state.phase = refs.phase.value;
        state.suppression = refs.suppression.value;

        var likelihood = scoreLikelihood(state);
        var severity = scoreSeverity(state);
        var bucketInfo = riskBucketFromScores(likelihood, severity);

        var likelihoodLevel = Math.max(1, Math.min(5, Math.ceil(likelihood / 2)));
        var severityLevel = Math.max(1, Math.min(5, Math.ceil(severity / 2)));

        Object.keys(cellsByIndex).forEach(function (key) {
          var cell = cellsByIndex[key];
          var parts = key.split(':');
          var row = Number(parts[0]);
          var col = Number(parts[1]);
          var active = row + 1 === likelihoodLevel && col + 1 === severityLevel;
          cell.classList.toggle('risk-cell-active', active);
          cell.style.background = active ? 'linear-gradient(135deg, rgba(34, 211, 238, 0.18), rgba(244, 63, 94, 0.18))' : '';
          cell.style.borderColor = active ? 'var(--cyan)' : 'var(--border)';
        });

        scoreValue.textContent = String(likelihoodLevel) + ' / ' + String(severityLevel);
        scoreLabel.textContent = 'LIKELIHOOD ' + likelihoodLevel + ' · SEVERITY ' + severityLevel;
        scoreLabel.className = 'risk-score-label ' + (bucketInfo.bucket === 'low' ? 'sev-nom' : bucketInfo.bucket === 'medium' ? 'sev-caution' : 'sev-warn');
        bucket.textContent = bucketInfo.label;
        bucket.style.borderColor = bucketInfo.color;
        bucket.style.color = bucketInfo.color;
        summary.textContent = 'Likelihood ' + likelihoodLevel + ' × Severity ' + severityLevel + ' = ' + bucketInfo.label + ' risk. O₂ concentration and ignition conditions dominate the hazard profile.';
        updateFlameBehavior(bucketInfo, likelihoodLevel, severityLevel);
      }

      ['o2', 'pressure', 'gravity', 'material', 'airflow', 'ignition', 'occupancy', 'phase', 'suppression'].forEach(function (key) {
        var el = refs[key];
        el.addEventListener('input', updateRisk);
        el.addEventListener('change', updateRisk);
      });

      updateRisk();

      return h('div', { class: 'card risk-card', 'aria-label': 'Mission risk estimator' }, [
        h('div', { class: 'cw-head' }, [
          h('h2', { class: 'cw-title', text: '⚠ NASA-style fire risk matrix' }),
          h('span', { class: 'ph-badge', text: 'Likelihood × Severity' })
        ]),
        h('div', { class: 'risk-grid' }, [
          h('div', { class: 'risk-controls' }, fieldRows.concat(selects)),
          h('div', { class: 'risk-matrix-panel' }, [
            h('div', { class: 'risk-matrix-result' }, [
              h('div', { class: 'risk-axes' }, [
                h('span', { text: 'Likelihood ↓' }),
                h('span', { text: 'Severity →' })
              ]),
              matrix,
              h('div', { class: 'risk-score-row' }, [
                h('div', { class: 'risk-score-box' }, [scoreValue, scoreLabel]),
                bucket
              ]),
              summary
            ]),
            h('div', { class: 'flame-behavior' }, [
              h('div', { class: 'flame-copy' }, [
                h('h3', { text: 'Crew-case flame sketch' }),
                flameCase,
                flameStateLabel,
                flameDescription,
                flameDrivers,
                h('p', { class: 'flame-disclaimer', text: 'Qualitative illustration only, not CFD or validated prediction. HSE bucket indicates crew consequence, not flame physics. Real shape also depends on fuel chemistry, geometry, ventilation and heat transfer.' })
              ]),
              h('div', { class: 'flame-figure' }, [flameSvg])
            ])
          ])
        ]),
        h('div', { class: 'risk-legend' }, [
          h('span', { text: 'O₂ / pressure / microgravity dominate' }),
          h('span', { text: 'Apollo 1 / Apollo 13 analogs' }),
          h('span', { text: '5×5 risk grid' })
        ]),
      ]);
    }

    el.appendChild(buildRiskCard());

 