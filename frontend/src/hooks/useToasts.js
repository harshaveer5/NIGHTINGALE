import { useCallback, useRef, useState } from "react";

let idCounter = 0;

export function useToasts() {
  const [toasts, setToasts] = useState([]);
  const timers = useRef({});

  const dismiss = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
    clearTimeout(timers.current[id]);
    delete timers.current[id];
  }, []);

  const push = useCallback(
    (message, type = "info", duration = 4000) => {
      const id = ++idCounter;
      setToasts((current) => [...current, { id, message, type }]);
      if (duration) {
        timers.current[id] = setTimeout(() => dismiss(id), duration);
      }
      return id;
    },
    [dismiss]
  );

  const runAction = useCallback(
    async (label, action, { silent = false } = {}) => {
      try {
        const result = await action();
        if (!silent) push(`${label} complete`, "success");
        return result;
      } catch (error) {
        push(error.message || `${label} failed`, "error", 6000);
        throw error;
      }
    },
    [push]
  );

  return { toasts, push, dismiss, runAction };
}
