'use client';

import { useState } from 'react';
import styles from "./SignInForm.module.css";
import Heading from "../Heading/Heading";
import { useRouter } from 'next/navigation';
import { decodeJwtRole } from '@/utils/auth';

export default function SigninForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false); // ✅ loading state
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true); // ✅ start loading

    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'accept': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await res.json();
      const token = data.token;
      if (!token) throw new Error('No token received');

      const role = decodeJwtRole(token);
      document.cookie = `token=${token}; path=/; max-age=86400`;

      if (role === 'candidate') {
        router.push('/userhome');
      } else if (role === 'recruiter') {
        router.push('/recruiterhome');
      } else {
        throw new Error('Unknown role in token');
      }
    } catch (err) {
      console.error('Login error:', err);
      setErrorMsg(err.message);
    } finally {
      setLoading(false); // ✅ end loading
    }
  };

  return (
    <main className={styles.main}>
      <div className={`${styles.container} ${styles.wrapper}`}>
        <div className={styles.formSection}>
          <Heading heading={"Login to Your Account"} />
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
              {loading ? 'Signing In...' : 'Sign In'}
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
