import React, { useState } from 'react';

const VerifyOTP = () => {
    const [email, setEmail] = useState("");
    const [code, setCode] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const response = await fetch("http://localhost:8000/api/auth/verify-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, otp: code }),
        });

        if (response.ok) {
            alert("Success! You can return to your terminal.");
        } else {
            alert("Invalid code.");
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '100px auto', textAlign: 'center' }}>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <input
                    type="email" placeholder="Email" value={email}
                    onChange={(e) => setEmail(e.target.value)} required
                />
                <input
                    type="text" placeholder="6-Digit Code" value={code}
                    onChange={(e) => setCode(e.target.value)} required
                />
                <button type="submit">Verify & Login CLI</button>
            </form>
        </div>
    );
};

export default VerifyOTP
