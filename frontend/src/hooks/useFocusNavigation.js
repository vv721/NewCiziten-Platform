export function useFocusNavigation() {
    const handleKeyDown = (e, nextRef, prevRef) => {

        const getTarget = (r) => (r && r.value ? r.value : r);

        const actions = {
            ArrowDown: () => getTarget(nextRef)?.focus(),
            ArrowUp: () => getTarget(prevRef)?.focus(),
        }

        if (actions[e.key]) {
            e.preventDefault()
            actions[e.key]()
        }
    }
    return { handleKeyDown }
}

