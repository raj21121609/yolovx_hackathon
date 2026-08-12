import { BrowserRouter, Routes, Route } from 'react-router-dom';

function Placeholder({ title }) {
  return <div style={{ padding: '20px' }}><h1>{title}</h1><p>Placeholder page</p></div>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Placeholder title="Login" />} />
        <Route path="/dashboard" element={<Placeholder title="Dashboard" />} />
        <Route path="/students" element={<Placeholder title="Students" />} />
        <Route path="/sessions" element={<Placeholder title="Sessions" />} />
        <Route path="/reports" element={<Placeholder title="Reports" />} />
        <Route path="*" element={<Placeholder title="Home - Please navigate to /login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
