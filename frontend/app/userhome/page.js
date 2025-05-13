// import Cookies from 'js-cookie';
import Banner from "@/components/Banner/Banner";
import CardHolder from "@/components/CardHolder/CardHolder";
import Heading from "@/components/Heading/Heading";
import Navbar from "@/components/Navbar/Navbar";
import Wrapper from "@/components/Wrapper/Wrapper";
import { cookies } from 'next/headers';

async function fetchJobs() {
    try {
        const response = await fetch('http://localhost:8000/jobs', {
            method: 'GET',
            headers: {
                'accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const jobs = await response.json();
        return jobs;
    } catch (error) {
        console.error('Error fetching jobs:', error);
        return null;
    }
}

async function fetchJobRecommendations(token) {
    try {
        const response = await fetch(`http://localhost:8000/match-scores/recommendations/uid`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const recommendations = await response.json();
        return recommendations;
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        return null;
    }
}

async function fetchRecommendedJobDetails(token) {
    try {
        const recommendations = await fetchJobRecommendations(token);
        if (!recommendations) {
            throw new Error("No recommendations found.");
        }

        const jobDetailsPromises = recommendations.map(async (rec) => {
            const response = await fetch(`http://localhost:8000/jobs/${rec.job_id}`, {
                method: 'GET',
                headers: {
                    'accept': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch job ${rec.job_id}: ${response.status}`);
            }

            const jobDetail = await response.json();
            return {
                ...jobDetail,
                highlighted: true,
                score: rec.score,
            };
        });

        const detailedJobs = await Promise.all(jobDetailsPromises);
        return detailedJobs;
    } catch (error) {
        console.error("Error fetching detailed job recommendations:", error);
        return [];
    }
}



export default async function UserHome() {
    const allJobsData = await fetchJobs();
    const kokkie = await cookies();
    const token = kokkie.get('token')?.value;
    const recommededJobsData = await fetchRecommendedJobDetails(token)
    return (
        <Wrapper>
            <Navbar navbarLinks={[]} />
            <Banner />
            <Heading heading={"All Jobs"} />
            <CardHolder jobs={allJobsData} />
            <Heading heading={"AI Recommended Jobs"} subheading={"This is the description!"} />
            <CardHolder jobs={recommededJobsData} />
        </Wrapper>
    );
}