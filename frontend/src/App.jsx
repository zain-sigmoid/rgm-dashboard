import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import Home from "./pages/home/Home";
import Toast from "./components/Toast";
import Alert from "./components/Alert";
import Navbar from "./components/Navbar";
import Scrolltotop from "./components/Scrolltotop";
import Wrong from "./pages/Wrong";
import About from "./pages/About";

const AppShell = () => {
  const host = "http://127.0.0.1:8000/api";
  const [alert, setAlert] = useState(null);
  const [toast, setToast] = useState(null);
  const location = useLocation();

  const showAlert = (message, type) => {
    setAlert({
      msg: message,
      type: type,
    });
    setTimeout(() => {
      setAlert(null);
    }, 3500);
  };

  const showToast = (content, copy = false, msg = "", variant = "primary") => {
    console.log(content, copy, msg);
    setToast({
      content,
      copy,
      msg,
      variant,
    });
  };

  const handleToastClose = () => {
    setToast(null);
  };

  return (
    <>
      <Navbar />
      <Scrolltotop />
      <Alert alert={alert} />
      {toast && (
        <Toast
          content={toast.content}
          copy={toast.copy}
          msg={toast.msg}
          variant={toast.variant}
          onClose={handleToastClose}
        />
      )}
      <Routes>
        <Route exact path="/" element={<Home />}></Route>
        <Route
          exact
          path="/:wrong"
          element={<Wrong prop={{ showAlert, showToast }} />}
        ></Route>
        <Route
          exact
          path="/about"
          element={<About prop={{ showAlert }} />}
        ></Route>
      </Routes>
    </>
  );
};

function App() {
  return (
    <Router>
      <AppShell />
    </Router>
  );
}

export default App;
