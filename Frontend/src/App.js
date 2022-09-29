import { CallApi } from "./Component/callApi";
import React from 'react'

function App() {
  return (
    <div>
      <CallApi />
      <div id='githubLinkDiv'>
        <a href="https://github.com/loganpederson/simcompaniescalculatorv2">See The Code!</a>
        or...
        <a href="https://www.buymeacoffee.com/loganpederson">☕Buy Me A Coffee?☕</a>
      </div>
    </div>
  );
}

export default App;