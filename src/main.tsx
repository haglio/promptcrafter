import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
import { schema } from './lib/schema';
// import { testSchema } from './test/fixtures/testSchema';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App schema={schema}/>
    {/* <App schema={testSchema}/> */}
  </React.StrictMode>,
);
