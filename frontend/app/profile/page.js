import ProfileForm from "@/components/ProfileForm/ProfileForm";
import Wrapper from "@/components/Wrapper/Wrapper";
import Navbar from "@/components/Navbar/Navbar";

export default function Profile() {
    return (
        <Wrapper>
            <Navbar navbarLinks={[{key: "Candidate Home", value: "/userhome"}, {key: "Logout", value: "/logout"}]} />
            <ProfileForm />
        </Wrapper>
    );
}