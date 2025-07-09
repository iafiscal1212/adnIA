import React from "react";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe("pk_test_TU_CLAVE_PUBLICA"); // ← PON aquí tu clave pública real de Stripe

const activarAdniaPro = async () => {
  const res = await fetch("http://localhost:3002/crear-sesion-pago", {
    method: "POST",
  });
  const data = await res.json();

  const stripe = await stripePromise;
  await stripe.redirectToCheckout({ sessionId: data.id });
};

export default function BotonAdniaPro() {
  return (
    <button
      onClick={activarAdniaPro}
      style={{
        padding: "12px 20px",
        backgroundColor: "#00ffd9",
        border: "none",
        borderRadius: "8px",
        fontWeight: "bold",
        cursor: "pointer",
        boxShadow: "0 0 10px #00ffd9",
        color: "#000",
      }}
    >
      🔓 Activar ADNIA PRO
    </button>
  );
}
