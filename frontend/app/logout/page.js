'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';

export default function LogoutPage() {
    const router = useRouter();

    useEffect(() => {
        Cookies.remove('token');      // ✅ Clear the token
        router.push('/');             // ✅ Redirect to home
    }, [router]);

    return <p>Logging you out...</p>; // Optional: temporary message
}
