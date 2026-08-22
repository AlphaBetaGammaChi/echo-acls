# EchoACLS — Air-Gapped Resuscitation Copilot & Clinical State Engine

An edge-native, zero-cloud clinical decision support tool designed for acute cardiac arrest ("Code Blue") and trauma resuscitations. Powered locally by **Google DeepMind MedGemma 4B** via Ollama.

---

## 🏗️ System Architecture Flow

```text
       [ Ambient Resuscitation Audio / Clinical Vitals Input ]
                                  │
                                  ▼
               [ Web Speech API / Audio Ingestion ]
                                  │
                                  ▼
      ┌─────────────────────────────────────────────────────────┐
      │         Air-Gapped Edge Runtime (No Cloud / PHI)        │
      │                                                         │
      │   MedGemma 4B (Ollama / Local Inference @ localhost)    │
      │     └─ Schema-Enforced Clinical Entity Extraction       │
      │     └─ ERC/AHA 2025 Algorithm Validation & 4H/4T Checks │
      │     └─ Hemodynamic & Quantitative Risk Scoring          │
      └─────────────────────────────────────────────────────────┘
                                  │
                                  ▼
      ┌─────────────────────────────────────────────────────────┐
      │         Interactive Resuscitation HUD & Timers          │
      │                                                         │
      │   • Dynamic Heart Rate & Ischemic SVG Mapping           │
      │   • 2-Minute CPR Rhythm Check Countdown                 │
      │   • Epinephrine Interval Timers (3–5 min cycle)         │
      │   • Standardized Scores (HEART, TIMI, Killip Class)     │
      └─────────────────────────────────────────────────────────┘
                                  │
                                  ▼
            [ Standardized HL7® FHIR JSON Export (NHS UK Core) ]
cat << 'EOF' > LICENSE
MIT License
Copyright (c) 2026 EchoACLS Contributors
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
