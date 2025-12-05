import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import UserState from "./context/UserState";
import Home from "./pages/home/Home";
import Toast from "./components/Toast";
import Alert from "./components/Alert";
import Navbar from "./components/Navbar";
import Scrolltotop from "./components/Scrolltotop";
import Wrong from "./pages/Wrong";
import PricingGlossary from "./pages/PricingGlossary";
import PromotionGlossary from "./pages/PromotionGlossary";
import Pricing from "./pages/pricing/Pricing";
import Promotion from "./pages/promotion/Promotion";

const AppShell = () => {
  const host = "http://127.0.0.1:8000/api";
  const [alert, setAlert] = useState(null);
  const [toast, setToast] = useState(null);

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
      <UserState prop={{ showAlert, showToast, host }}>
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
          <Route exact path="/smart-pricing" element={<Pricing />} />
          <Route
            exact
            path="/optimal-promotion"
            element={<Promotion prop={{ showAlert, showToast }} />}
          />
          <Route exact path="/glossary/pricing" element={<PricingGlossary />} />
          <Route
            exact
            path="/glossary/promotion"
            element={<PromotionGlossary />}
          />
          <Route
            exact
            path="/:wrong"
            element={<Wrong prop={{ showAlert, showToast }} />}
          ></Route>
        </Routes>
      </UserState>
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
