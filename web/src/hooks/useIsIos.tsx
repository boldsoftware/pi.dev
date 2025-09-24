import { useState, useEffect } from "react";

export function useIsIos() {
  const [isIOS, setIsIOS] = useState(false);

  useEffect(() => {
    setIsIOS(
      typeof window !== "undefined" &&
        /iPad|iPhone|iPod/.test(navigator.userAgent),
    );
  }, []);

  return isIOS;
}
