import { useState } from "react";
import Editor from "@monaco-editor/react";
import { useEditorStore } from "@/store/Store";
import Split from "react-split";
import "./split.css";

const TextEditor = () => {
  const { code, setCode } = useEditorStore();
  const [theme, setTheme] = useState("vs-dark");

  return (
    <>
      <button
        onClick={() => setTheme(theme === "vs-dark" ? "vs" : "vs-dark")}
        className="mb-2 px-3 py-1 bg-gray-700 text-white rounded"
      >
        Toggle Theme
      </button>

      <div style={{ height: "50vh" }}>
        <Split className="split" sizes={[50, 50]} minSize={200} gutterSize={6}>
          <Editor
            height="400px"
            language="javascript"
            value={code}
            theme={theme}
            onChange={(value) => setCode(value ?? "")}
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
            }}
          />

          <div className="flex flex-col p-2">
            <div className="flex flex-col mb-2">
              <h2 className="text-black dark:text-white font-bold">
                AI Suggestion
              </h2>
              <button className="px-2 py-1 bg-gray-500 text-white rounded">
                Turn Off AI
              </button>
            </div>
            <div className="flex-1 bg-slate-400 p-2 rounded">Use for loop</div>
          </div>
        </Split>

        <div className="mt-2 p-2 font-semibold text-black dark:text-white">
          Problem Statement
        </div>
      </div>
    </>
  );
};

export default TextEditor;
