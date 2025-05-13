import SignUpForm from "@/components/SignUpForm/SignUpForm";
import Wrapper from "@/components/Wrapper/Wrapper";
import Navbar from "@/components/Navbar/Navbar";

export default function SignInPage() {
    return (
        <Wrapper>
            <Navbar navbarLinks={[{ key: "SignIn", value: "/signin" }]} />
            <SignUpForm />
        </Wrapper>
    )
}