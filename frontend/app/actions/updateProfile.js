import Cookies from 'js-cookie';

export async function updateProfile(formData) {
    const token = Cookies.get('token');

    const body = {
        full_name: formData.get('full_name'),
        phone_number: formData.get('phone_number'),
        location: formData.get('location'),
        years_of_experience: parseInt(formData.get('years_of_experience') || '0', 10),
        key_skills: formData.get('key_skills')?.split(',').map(s => s.trim()).filter(Boolean) || [],
    };

    const response = await fetch('http://localhost:8000/users/me', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(body),
        cache: 'no-store',
    });

    if (!response.ok) {
        console.error(`Failed to update profile: ${response.status}`);
        return;
    }

    const result = await response.json();
}
