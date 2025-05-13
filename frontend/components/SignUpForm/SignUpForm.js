'use client';

import { useState } from 'react';
import styles from "./SignUpForm.module.css"; // Reuse same styling
import Heading from "../Heading/Heading";
import { useRouter } from 'next/navigation';
import { decodeJwtRole } from '@/utils/auth';

export default function SignUpForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false); // 🆕 loading state
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true); // 🆕 start loading

    try {
      // Step 1: Sign up the user
      const signupRes = await fetch('http://localhost:8000/auth/signup/candidate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'accept': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!signupRes.ok) {
        const errorData = await signupRes.json();
        throw new Error(errorData.detail || 'Signup failed');
      }

      // Step 2: Log in the user
      const loginRes = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'accept': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!loginRes.ok) {
        const errorData = await loginRes.json();
        throw new Error(errorData.detail || 'Login after signup failed');
      }

      const loginData = await loginRes.json();
      const token = loginData.token;
      if (!token) throw new Error('No token received after signup');

      const role = decodeJwtRole(token);
      document.cookie = `token=${token}; path=/; max-age=86400`;

      if (role === 'candidate') {
        router.push('/userhome');
      } else {
        throw new Error('Unexpected role');
      }

    } catch (err) {
      console.error('Signup error:', err);
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      <div className={`${styles.container} ${styles.wrapper}`}>
        <div className={styles.formSection}>
          <Heading heading={"Create Your Account"} />
          <form className={styles.form} onSubmit={handleSubmit}>
            <input
              type="email"
              placeholder="Email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
            <input
              type="password"
              placeholder="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
            {errorMsg && <p className={styles.error}>{errorMsg}</p>}
            <button type="submit" disabled={loading}>
              {loading ? 'Signing Up...' : 'Sign Up'}
            </button>
          </form>
        </div>
        <div className={styles.imageSection}>
          <img
            src="https://firebase.google.com/static/images/brand-guidelines/logo-vertical.png"
            alt="Signup Visual"
          />
        </div>
      </div>
    </main>
  );
}
