import Wrapper from "@/components/Wrapper/Wrapper";
import Navbar from "@/components/Navbar/Navbar";
import NewJobForm from "@/components/NewJobForm/NewJobForm";

export default function NewJob() {
    return (
        <Wrapper>
            <Navbar navbarLinks={[{key: "Recruiter Home", value: "/recruiterhome"}, {key: "Logout", value: "/logout"}]} />
            <NewJobForm />
        </Wrapper>
    );
}