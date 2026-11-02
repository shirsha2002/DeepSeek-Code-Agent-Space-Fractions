# DeepSeek-Code-Agent-Space-Fractions

Task 1 delivery: a Windows desktop code agent that turns two architecture documents into a working desktop project using the official DeepSeek API (`deepseek-v4-pro`).

| Path | What it is |
| --- | --- |
| `Task1CodeAgent.exe` | The code agent (standalone Windows exe, no Python needed). Enter your own DeepSeek API key in the app; it is never saved. |
| `inputs/` | The two task inputs: `Architecture_Documentation.md` and `Architecture_View.md`. |
| `output/run_/20261102T140304Z_ec0d0c74/` | The live run shown in the demo video: generated Space Fractions game (`project/`), the model's original responses (`manifest_0.json`, `manifest_1.json`), static checks, test results and the run summary. One automatic repair; no manual edits. |

Agent source code, tests, build scripts and the technical report: https://github.com/shirsha2002/agent-space-fractions

## Run the generated game from source

```
cd output/run_/20261102T140304Z_ec0d0c74/project
python main.py
python -m unittest discover -s tests
```
